import re
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = re.sub(r'[^a-zA-Z]', ' ', text)   # keep only letters
    return text.lower()

def get_vectorizer(max_features=5000):
    """Return a TF-IDF vectorizer."""
    return TfidfVectorizer(max_features=max_features, stop_words='english')
