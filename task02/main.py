import time
import random
from typing import Dict

class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        """
        :param min_interval: minimum seconds required between messages from the same user
        """
        self.min_interval = min_interval
        # store last message timestamp per user
        self.last_message_time: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        """
        Returns True if user can send a new message at current time, False otherwise.
        """
        now = time.time()
        last_time = self.last_message_time.get(user_id)
        # if never sent before or enough time passed
        if last_time is None or (now - last_time) >= self.min_interval:
            return True
        return False

    def record_message(self, user_id: str) -> bool:
        """
        Attempts to record a message for the user.
        Returns True if message is recorded (allowed), False if rate-limited.
        """
        now = time.time()
        if self.can_send_message(user_id):
            self.last_message_time[user_id] = now
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Returns time in seconds until the user can send the next message.
        0.0 if user can send immediately.
        """
        now = time.time()
        last_time = self.last_message_time.get(user_id)
        if last_time is None:
            return 0.0
        elapsed = now - last_time
        wait = self.min_interval - elapsed
        return max(wait, 0.0)


def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = str(message_id % 5 + 1)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        status = '✓' if result else f'× (очікування {wait_time:.1f}с)'
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))

    print("\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = str(message_id % 5 + 1)
        result = limiter.record_message(user_id)
        wait_time = limiter.time_until_next_allowed(user_id)
        status = '✓' if result else f'× (очікування {wait_time:.1f}с)'
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | {status}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()