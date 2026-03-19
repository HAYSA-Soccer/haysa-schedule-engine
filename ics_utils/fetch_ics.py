import requests

def fetch_ics(url: str) -> str:
    """
    Downloads an ICS file from the given URL and returns its text content.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

if __name__ == "__main__":
    # Temporary test URL — replace with your real SSSL feed
    TEST_URL = "https://example.com/schedule.ics"
    print(fetch_ics(TEST_URL))
