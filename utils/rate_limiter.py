import time
from threading import Lock


class RateLimiter:
    def __init__(self, rate_limit_per_second):
        self.rate_limit = rate_limit_per_second
        self.allowance = 1.0  # Start with the full allowance
        self.last_check = time.monotonic()
        self.lock = (
            Lock()
        )  # Lock to prevent race conditions in a multi-threaded environment

    def can_proceed(self):
        # Assumes the rate-limited function is called as soon as can_proceed() returns True
        with self.lock:
            current_time = time.monotonic()
            time_passed = current_time - self.last_check

            # Calculate the new allowance based on the time passed
            self.allowance += time_passed * self.rate_limit
            self.last_check = current_time

            # Check if there is enough allowance to proceed
            if self.allowance >= 1.0:
                self.allowance = 0.0
                return True
            return False

    def wait_until_can_proceed(self):
        while not self.can_proceed():
            time.sleep(0.1)
