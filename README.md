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
| Argument                   | Description                                                             |
| -------------------------- | ----------------------------------------------------------------------- |
| `protocol`                 | Target protocol: `ftp`, `ssh`, `telnet`, `rdp`, `smb`, `http`           |
| `-t`, `--target`           | IP address or hostname of the target                                    |
| `-p`, `--port`             | Target port (optional, defaults based on protocol)                      |
| `-c`, `--combos`           | Path to combo list file (`username:password`)                           |
| `-u`, `--http-url`         | Login form URL (required for HTTP protocol)                             |
| `--uf`                     | HTTP form field name for **username** (default: `username`)             |
| `--pf`                     | HTTP form field name for **password** (default: `password`)             |
| `-k`, `--http-success-key` | Keyword in HTTP response indicating successful login                    |
| `-w`, `--max-workers`      | Max concurrent threads (default: `10`)                                  |
| `-e`, `--max-errors`       | Max number of errors before stopping (default: `10`)                    |
| `-o`, `--output`           | Output file name prefix (default: `output`)                             |
| `-s`, `--save`             | Save valid credentials to file                                          |
| `--fmt`                    | Output format: `json`, `csv`, `both`, or `console` (default: `console`) |
| `-l`, `--logfile`          | Log file name (default: `brute.log`)                                    |
| `--px`                     | Enable SOCKS5 proxy server                                              |
| `--pp`                     | SOCKS5 proxy port (default: `1080`)                                     |
