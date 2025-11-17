"""
Simple Fake News Classifier with Sentiment Analysis
Features: TF-IDF + VADER Sentiment
Fast, clean, beginner-friendly
"""

import pandas as pd
import numpy as np
import pickle
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()


def preprocess_text(text):
    """Clean text - lowercase and remove special characters"""
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    return text


def get_sentiment_features(text):
    """
    Get sentiment scores using VADER
    Returns 4 scores: positive, negative, neutral, compound
    """
    scores = sentiment_analyzer.polarity_scores(str(text))
    return [
        scores['pos'],
        scores['neg'],
        scores['neu'],
        scores['compound']
    ]


def get_entity_features(text):
    """Placeholder - returns zeros for compatibility"""
    return [0, 0, 0, 0]


def get_text_stats(text):
    """
    Basic text statistics
    Helps detect clickbait patterns
    """
    text = str(text)
    words = text.split()
    
    return [
        len(words),
        np.mean([len(w) for w in words]) if words else 0,
        sum(1 for c in text if c.isupper()) / len(text) if text else 0,
        text.count('!'),
        text.count('?')
    ]


def train_and_save():
    """Train the classifier"""
    
    print("Loading data...")
    
    fake = pd.read_csv("busted_ml/data/Fake.csv")
    real = pd.read_csv("busted_ml/data/Real.csv")
    
    fake['label'] = 0
    real['label'] = 1
    
    df = pd.concat([fake, real], ignore_index=True)
    print(f"Loaded {len(df):,} articles")
    
    # Clean text
    print("Cleaning text...")
    df['clean_text'] = df['text'].apply(preprocess_text)
    
    # Extract sentiment features
    print("Analyzing sentiment...")
    sentiment_list = df['text'].apply(get_sentiment_features).tolist()
    sentiment_array = np.array(sentiment_list)
    
    # Extract text stats
    print("Extracting text statistics...")
    stats_list = df['text'].apply(get_text_stats).tolist()
    stats_array = np.array(stats_list)
    
    # Combine numerical features
    numerical_features = np.hstack([
        sentiment_array,
        np.zeros((len(df), 4)),  # Entity placeholder
        stats_array
    ])
    
    # Show sentiment differences
    print("\nSentiment Analysis Results:")
    print("              Positive  Negative  Neutral   Compound")
    fake_sent = sentiment_array[df['label'] == 0].mean(axis=0)
    real_sent = sentiment_array[df['label'] == 1].mean(axis=0)
    print(f"Fake news:    {fake_sent[0]:.3f}     {fake_sent[1]:.3f}     {fake_sent[2]:.3f}     {fake_sent[3]:.3f}")
    print(f"Real news:    {real_sent[0]:.3f}     {real_sent[1]:.3f}     {real_sent[2]:.3f}     {real_sent[3]:.3f}")
    
    # Split data
    X_train_text, X_test_text, X_train_num, X_test_num, y_train, y_test = train_test_split(
        df['clean_text'],
        numerical_features,
        df['label'],
        test_size=0.2,
        random_state=42,
        stratify=df['label']
    )
    
    # TF-IDF
    print("\nVectorizing text...")
    vectorizer = TfidfVectorizer(
        max_features=2000,
        min_df=5,
        max_df=0.7,
        ngram_range=(1, 2)
    )
    
    X_train_tfidf = vectorizer.fit_transform(X_train_text)
    X_test_tfidf = vectorizer.transform(X_test_text)
    
    # Combine features
    X_train = np.hstack([X_train_tfidf.toarray(), X_train_num])
    X_test = np.hstack([X_test_tfidf.toarray(), X_test_num])
    
    print(f"Total features: {X_train.shape[1]}")
    
    # Train model
    print("\nTraining Logistic Regression...")
    model = LogisticRegression(max_iter=200, random_state=42, C=1.0)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy: {acc:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Fake', 'Real']))
    
    # Save
    print("\nSaving model...")
    os.makedirs("busted_ml/models", exist_ok=True)
    
    with open("busted_ml/models/model.pkl", "wb") as f:
        pickle.dump(model, f)
    
    with open("busted_ml/models/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    print("Model saved successfully!")
    print("\nTraining complete. You can now run app.py")


if __name__ == "__main__":
    train_and_save()