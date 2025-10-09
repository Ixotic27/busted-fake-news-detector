import joblib
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

def train_naive_bayes(X_train, y_train):
    """Train a Naive Bayes classifier."""
    model = MultinomialNB()
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate accuracy of the trained model."""
    y_pred = model.predict(X_test)
    return accuracy_score(y_test, y_pred)

def save_model(model, vectorizer, model_path="busted_ml/models/fake_news_nb.pkl", vec_path="busted_ml/models/tfidf.pkl"):
    """Save trained model + vectorizer."""
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vec_path)

def load_model(model_path="busted_ml/models/fake_news_nb.pkl", vec_path="busted_ml/models/tfidf.pkl"):
    """Load trained model + vectorizer."""
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    return model, vectorizer
