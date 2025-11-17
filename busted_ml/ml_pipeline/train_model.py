"""
Uses TF-IDF + Sentiment + Classical ML(No Deep Learning)
"""
import pandas as pd
import numpy as np
import os
import pickle

# ML
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# NLP
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy

# NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

sentiment_analyzer = SentimentIntensityAnalyzer()


# Text preprocessing
def preprocess_text(text):
    text = str(text).lower()

    import re
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_words and len(w) > 2]

    lem = WordNetLemmatizer()
    tokens = [lem.lemmatize(w) for w in tokens]

    return " ".join(tokens)


# Sentiment features
def get_sentiment_features(text):
    scores = sentiment_analyzer.polarity_scores(str(text))
    return {
        'sentiment_pos': scores['pos'],
        'sentiment_neg': scores['neg'],
        'sentiment_neu': scores['neu'],
        'sentiment_compound': scores['compound']
    }


# Entity features
def get_entity_features(text):
    if nlp is None:
        return {'entity_count': 0, 'person_count': 0, 'org_count': 0, 'gpe_count': 0}

    doc = nlp(str(text)[:100000])
    return {
        'entity_count': len(doc.ents),
        'person_count': sum(1 for e in doc.ents if e.label_ == 'PERSON'),
        'org_count': sum(1 for e in doc.ents if e.label_ == 'ORG'),
        'gpe_count': sum(1 for e in doc.ents if e.label_ == 'GPE')
    }


# Simple text statistics
def get_text_stats(text):
    text = str(text)
    words = text.split()

    return {
        'word_count': len(words),
        'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
        'caps_ratio': sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0,
        'exclamation_count': text.count('!'),
        'question_count': text.count('?')
    }


def train_and_save():
    print("Loading data...")

    fake = pd.read_csv("busted_ml/data/Fake.csv")
    real = pd.read_csv("busted_ml/data/Real.csv")

    fake['label'] = 0
    real['label'] = 1

    df = pd.concat([fake, real], ignore_index=True)
    df['clean_text'] = df['text'].apply(preprocess_text)

    sentiment_df = pd.DataFrame(df['text'].apply(get_sentiment_features).tolist())
    entity_df = pd.DataFrame(df['text'].apply(get_entity_features).tolist())
    stats_df = pd.DataFrame(df['text'].apply(get_text_stats).tolist())

    feature_df = pd.concat([sentiment_df, entity_df, stats_df], axis=1)

    X_train_text, X_test_text, X_train_feat, X_test_feat, y_train, y_test = train_test_split(
        df['clean_text'],
        feature_df,
        df['label'],
        test_size=0.2,
        random_state=42,
        stratify=df['label']
    )

    vectorizer = TfidfVectorizer(
        max_features=3000,
        min_df=5,
        max_df=0.7,
        ngram_range=(1, 2),
        sublinear_tf=True
    )

    X_train_tfidf = vectorizer.fit_transform(X_train_text)
    X_test_tfidf = vectorizer.transform(X_test_text)

    X_train_combined = np.hstack([X_train_tfidf.toarray(), X_train_feat.values])
    X_test_combined = np.hstack([X_test_tfidf.toarray(), X_test_feat.values])

    print("Training models...")

    nb_model = MultinomialNB(alpha=0.1)
    nb_model.fit(X_train_combined, y_train)
    nb_acc = accuracy_score(y_test, nb_model.predict(X_test_combined))

    lr_model = LogisticRegression(max_iter=1000)
    lr_model.fit(X_train_combined, y_train)
    lr_acc = accuracy_score(y_test, lr_model.predict(X_test_combined))

    best_model = lr_model if lr_acc > nb_acc else nb_model
    best_acc = max(nb_acc, lr_acc)

    print("Best model accuracy:", round(best_acc * 100, 2), "%")

    os.makedirs("busted_ml/models", exist_ok=True)

    pickle.dump(best_model, open("busted_ml/models/model.pkl", "wb"))
    pickle.dump(vectorizer, open("busted_ml/models/vectorizer.pkl", "wb"))
    pickle.dump(feature_df.columns.tolist(), open("busted_ml/models/feature_columns.pkl", "wb"))

    return best_model, vectorizer, feature_df.columns


if __name__ == "__main__":
    train_and_save()
