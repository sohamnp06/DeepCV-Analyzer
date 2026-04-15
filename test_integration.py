import os
from config import load_env_file
from models.embedding_model import get_embedding

load_env_file()

def test_single_embedding():
    print("Testing single string embedding...")
    text = "Machine learning engineer"
    vector = get_embedding(text)
    if isinstance(vector, list) and len(vector) > 0:
        print(f"Success! Vector length: {len(vector)}")
        print(f"First 5 values: {vector[:5]}")
    else:
        print("Failed to get valid vector.")

def test_batch_embedding():
    print("\nTesting batch (list of strings) embedding...")
    texts = ["Python developer", "Software engineering"]
    vectors = get_embedding(texts)
    if isinstance(vectors, list) and len(vectors) == 2:
        print(f"Success! Received {len(vectors)} vectors.")
        print(f"Vector 1 length: {len(vectors[0]) if vectors[0] else 'empty'}")
    else:
        print("Failed to get valid batch vectors.")

if __name__ == "__main__":
    if not os.getenv("HUGGINGFACE_API_KEY"):
        print("Warning: HUGGINGFACE_API_KEY not found in environment.")
    
    try:
        test_single_embedding()
        test_batch_embedding()
    except Exception as e:
        print(f"Error during testing: {e}")
