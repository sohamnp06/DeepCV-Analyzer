from sentence_transformers import SentenceTransformer

# Load once globally (IMPORTANT for performance)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def get_embedding(text):
    return model.encode(text)