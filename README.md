# Fuxnet
- Fuxnet is a modular brute force tool that supports various network protocols such as
- FTP, SSH, Telnet, RDP, SMB, and HTTP. Equipped with SOCKS5 proxy support,
- logging, as well as the option to save results in JSON/CSV format.
---
## Current Key Features 
- Supported protocols: FTP, SSH, Telnet, RDP, SMB, HTTP

- Parallel bruteforce using ThreadPoolExecutor

- Optional SOCKS5 proxy server

- Flexible output: console, json, csv, or both

- Complete logging of activity to file
---
### Complete Options List
```bash
protocol  	     Protokol target (ftp, ssh, telnet, rdp, smb, http)
--target             IP or target hostname
--port               Target port (optional, default based on protocol)
--combos             Path to user:pass combo file
--http-url           URL form login (khusus HTTP)
--http-user-field    Name field password (default: password)
--http-success-key   Keywords in the response that indicate successful login
--max-workers        Maximum number of threads (default: 10)
--max-errors         Maximum number of errors before stopping (default: 10)
--output	     Prefix name file output (default: output)
--save               Save the results to a file
--output-format	     Format output: json, csv, both, console
--logfile.           File log (default: brute.log)
--use-proxy          Enable SOCKS5 proxy
--proxy-port	     Port proxy (default: 1080)
```
# Basic Usage
```bash
python3 Fuxnet.py <protocol> --target <ip/host> --combos <name and path file>
```
