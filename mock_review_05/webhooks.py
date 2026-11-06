import time
import requests


def deliver_webhook(url: str, payload: dict, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code < 500:
                return True
        except requests.RequestException:
            pass
        time.sleep(2 ** attempt)
    return False
