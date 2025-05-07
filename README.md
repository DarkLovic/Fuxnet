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
protocol  	Protokol target (ftp, ssh, telnet, rdp, smb, http)
--target    IP or target hostname
--port      Target port (optional, default based on protocol)
--combos    Path ke file combo user:pass
--http-url  URL form login (khusus HTTP)
Nama field password (default: password)
--http-user-field 
