import re
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_text(txt):
    """Clean text - remove special chars, lowercase"""
    if not txt or txt == "N/A":
        return ""
    txt = re.sub(r'[^a-zA-Z\s]', ' ', txt)  # keep letters and spaces
    txt = re.sub(r'\s+', ' ', txt)  # remove extra spaces
    return txt.lower().strip()

def get_vectorizer(max_feat=5000):
    """Create TF-IDF vectorizer"""
    return TfidfVectorizer(
        max_features=max_feat,
        stop_words='english',
        ngram_range=(1, 2),  # unigrams + bigrams
        min_df=2  # ignore very rare words
    )

def preprocess_data(texts):
    """Clean list of texts"""
    return [clean_text(t) for t in texts]