"""
Prediction module for Flask app
Works with train_model.py functions
"""

import numpy as np
import pickle

# Import feature functions from training module
from busted_ml.ml_pipeline.train_model import (
    preprocess_text,
    get_sentiment_features,
    get_entity_features,
    get_text_stats
)

# Paths
MODEL_PATH = "busted_ml/models/model.pkl"
VEC_PATH = "busted_ml/models/vectorizer.pkl"


def load_assets():
    """Load trained model and vectorizer"""
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(VEC_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    return model, vectorizer


# Load model once at startup
model, vectorizer = load_assets()


def build_feature_vector(text):
    """
    Convert input text into the same structure used during training:
    TF-IDF + sentiment + entity features + text statistics
    """
    # Preprocess and vectorize text
    clean = preprocess_text(text)
    tfidf_vec = vectorizer.transform([clean]).toarray()
    
    # Extract numerical features
    f_sent = get_sentiment_features(text)
    f_ent = get_entity_features(text)
    f_stats = get_text_stats(text)
    
    # Combine all numerical features
    numeric_features = np.hstack([f_sent, f_ent, f_stats]).reshape(1, -1)
    
    # Combine TF-IDF + numerical
    final_vector = np.hstack([tfidf_vec, numeric_features])
    
    return final_vector


def run_prediction(text):
    """
    Main prediction function called by Flask app
    
    Returns:
        dict with prediction, confidence, and reason
    """
    # Build feature vector
    vec = build_feature_vector(text)
    
    # Get prediction (0=fake, 1=real)
    pred = model.predict(vec)[0]
    
    # Get probability
    proba = model.predict_proba(vec)[0]
    confidence = float(max(proba))
    
    # Format result
    label = "REAL" if pred == 1 else "FAKE"
    
    reason = (
        "Text aligns with features commonly seen in real news."
        if pred == 1 else
        "Text shows multiple signs of misinformation based on training patterns."
    )
    
    return {
        "prediction": label,
        "confidence": confidence,
        "reason": reason
    }


def predict_with_details(text):
    """
    Extended prediction with sentiment breakdown
    Useful for debugging or detailed analysis
    """
    # Get standard prediction
    result = run_prediction(text)
    
    # Add sentiment details
    sentiment = get_sentiment_features(text)
    result['sentiment'] = {
        'positive': sentiment[0],
        'negative': sentiment[1],
        'neutral': sentiment[2],
        'compound': sentiment[3]
    }
    
    # Add text stats
    stats = get_text_stats(text)
    result['text_stats'] = {
        'word_count': stats[0],
        'avg_word_length': stats[1],
        'caps_ratio': stats[2],
        'exclamation_count': stats[3],
        'question_count': stats[4]
    }
    
    return result


if __name__ == "__main__":
    # Test prediction
    test_text = "SHOCKING NEWS! You won't believe this!!!"
    result = predict_with_details(test_text)
    
    print("\nTest Prediction:")
    print(f"Text: {test_text}")
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Text Stats: {result['text_stats']}")