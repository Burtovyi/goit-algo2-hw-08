import random
import time
from typing import Dict
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        """
        :param window_size: size of time window in seconds
        :param max_requests: maximum allowed requests per user within window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        # store for each user a deque of timestamp floats
        self.user_windows: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """
        Remove timestamps older than the sliding window for a user.
        If no timestamps remain, remove the user's entry entirely.
        """
        if user_id not in self.user_windows:
            return
        window = self.user_windows[user_id]
        # pop left while oldest is outside the window
        cutoff = current_time - self.window_size
        while window and window[0] <= cutoff:
            window.popleft()
        # if window is empty, remove user
        if not window:
            del self.user_windows[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """
        Check if the user can send a message at current time.
        Returns True if under limit, False if limit reached.
        """
        now = time.time()
        self._cleanup_window(user_id, now)
        # if user has fewer than max_requests in window, allowed
        if user_id not in self.user_windows or len(self.user_windows[user_id]) < self.max_requests:
            return True
        return False

    def record_message(self, user_id: str) -> bool:
        """
        Record a message for the user if allowed.
        Returns True if recorded (allowed), False otherwise.
        """
        now = time.time()
        self._cleanup_window(user_id, now)
        if self.can_send_message(user_id):
            # initialize deque if first message
            if user_id not in self.user_windows:
                self.user_windows[user_id] = deque()
            # append current timestamp
            self.user_windows[user_id].append(now)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Returns seconds until the user can send next message.
        If user is allowed now or has no record, returns 0.0.
        """
        now = time.time()
        # clean up old timestamps first
        self._cleanup_window(user_id, now)
        if user_id not in self.user_windows:
            return 0.0
        window = self.user_windows[user_id]
        # if under limit, can send immediately
        if len(window) < self.max_requests:
            return 0.0
        # else, next allowed is when the oldest timestamp exits the window
        oldest = window[0]
        wait = oldest + self.window_size - now
        return max(wait, 0.0)

# Демонстрація роботи

def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = str(message_id % 5 + 1)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        status = '✓' if result else f'× (очікування {wait_time:.1f}с)'
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = str(message_id % 5 + 1)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        status = '✓' if result else f'× (очікування {wait_time:.1f}с)'
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
