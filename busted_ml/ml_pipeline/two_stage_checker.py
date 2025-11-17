import pickle
import numpy as np
import pandas as pd

from busted_ml.ml_pipeline.train_model import (
    preprocess_text,
    get_sentiment_features,
    get_entity_features,
    get_text_stats
)

from busted_ml.scraper.google_news_checker import search_google_news, check_domain

# Load ML model + vectorizer + feature columns
model = pickle.load(open("busted_ml/models/model.pkl", "rb"))
vectorizer = pickle.load(open("busted_ml/models/vectorizer.pkl", "rb"))
feature_columns = pickle.load(open("busted_ml/models/feature_columns.pkl", "rb"))


def ml_predict(text):
    """Runs ML prediction using logistic regression + all NLP features."""

    clean = preprocess_text(text)

    sent = get_sentiment_features(text)
    ents = get_entity_features(text)
    stats = get_text_stats(text)

    num_feats = pd.DataFrame([{**sent, **ents, **stats}])
    num_feats = num_feats.reindex(columns=feature_columns, fill_value=0)

    tfidf_vec = vectorizer.transform([clean]).toarray()

    final_vector = np.hstack([tfidf_vec, num_feats.values])

    pred = model.predict(final_vector)[0]
    prob = model.predict_proba(final_vector)[0][pred]

    return "REAL" if pred == 1 else "FAKE", float(prob)


def check_news(text, input_url=None):
    """
    2-stage verification:
    Stage 1: ML prediction (Naive Bayes removed → Logistic only)
    Stage 2: Google News search + domain check
    """

    # Stage 1 — ML judging
    ml_pred, confidence = ml_predict(text)

    # Stage 2 — Web verification using Google News RSS
    verified = search_google_news(text)

    # Domain credibility check (if URL provided)
    domain_status = None
    if input_url:
        domain_status = check_domain(input_url)

    # FINAL DECISION LOGIC
    if verified:
        final_pred = "REAL (Verified Online)"
        reason = "This news appears on trusted Google News sources."
        stage = "ML + Web Verification"
    elif ml_pred == "REAL":
        final_pred = "LIKELY REAL (ML Only)"
        reason = "ML suggests it is real, but no online matches were found."
        stage = "ML Only"
    else:
        final_pred = "FAKE / UNVERIFIED"
        reason = "ML classified as fake and no trusted sources reported it."
        stage = "ML + Web Check"

    return {
        "prediction": final_pred,
        "confidence": confidence,
        "stage": stage,
        "reason": reason,
        "ml_says": ml_pred,
        "verified_sources": verified,
        "domain_status": domain_status
    }
