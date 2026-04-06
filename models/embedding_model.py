import os
import time
import logging
import requests

logger = logging.getLogger(__name__)

# The router URL for the model ID directly
API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"

def get_embedding(text):
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    headers = {
        "X-Wait-For-Model": "true",
        "X-Use-Cache": "true"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    # Attempt to force feature-extraction task
    headers["X-Task"] = "feature-extraction"
        
    payload = {"inputs": text}
    
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 503:
                time.sleep(2)
                continue
            
            # If 400 specifically on MiniLM, it might be due to Task mapping. 
            # We use an alternative 384-dim model that defaults to feature-extraction as a fallback.
            if response.status_code == 400:
                fallback_url = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"
                response = requests.post(fallback_url, headers=headers, json=payload, timeout=20)

            if response.status_code == 200:
                data = response.json()
                # Standardization: ensure it returns the vector(s)
                return data
            else:
                logger.error(f"HF API Error {response.status_code}: {response.text}")
                break
        except Exception as e:
            logger.error(f"HF API Request failed: {e}")
            time.sleep(1)
            
    return [] if isinstance(text, str) else [[] for _ in text]