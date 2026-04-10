import requests

def fetch_ics(url: str) -> str:
    """
    Downloads an ICS file from the given URL and returns its text content.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        )
    }

    print(f"Fetching ICS from: {url}")

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

if __name__ == "__main__":
    TEST_URL = "https://example.com/schedule.ics"
    print(fetch_ics(TEST_URL))
