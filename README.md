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
## How to Run
- Format Combo List
- The combo file must be a user:pass list in the following format:
```bash
admin:admin123
username:password 
...
