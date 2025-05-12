import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("CREWAI_API_URL_1")
BEARER_TOKEN = os.getenv("CREWAI_BEARER_TOKEN_1")

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

def get_inputs():
    url = f"{API_URL}/inputs"
    response = requests.get(url, headers=headers)
    if response.ok:
        print("Inputs:")
        print(response.json())
    else:
        print(f"Failed to get inputs: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    get_inputs() 