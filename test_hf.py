import os
import requests
from config import load_env_file

load_env_file()

API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"

headers = {
    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"
}

data = {
    "inputs": {
        "source_sentence": "Machine learning engineer",
        "sentences": ["Python developer with NLP experience"]
    }
}

response = requests.post(API_URL, headers=headers, json=data)

print("Status:", response.status_code)
print("Response:", response.json())