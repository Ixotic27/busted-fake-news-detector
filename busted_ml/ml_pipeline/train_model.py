import pandas as pd
from sklearn.model_selection import train_test_split
from busted_ml.ml_pipeline.preprocess import clean_text, get_vectorizer
from busted_ml.ml_pipeline.model import train_naive_bayes, evaluate_model, save_model

def train_and_save():
    """Train model on Fake.csv and Real.csv"""
    # Load datasets
    fake = pd.read_csv("busted_ml/data/Fake.csv")
    real = pd.read_csv("busted_ml/data/Real.csv")
    
    # Add labels
    fake['label'] = "fake"
    real['label'] = "real"
    
    # Merge
    df = pd.concat([fake, real], axis=0).reset_index(drop=True)
    
    # Clean text
    df['clean_text'] = df['text'].apply(clean_text)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        df['clean_text'], df['label'], test_size=0.2, random_state=42
    )
    
    # Vectorize
    vec = get_vectorizer()
    X_train_vec = vec.fit_transform(X_train)
    X_test_vec = vec.transform(X_test)
    
    # Train
    model = train_naive_bayes(X_train_vec, y_train)
    
    # Evaluate
    acc = evaluate_model(model, X_test_vec, y_test)
    print(f"✅ Model Accuracy: {acc:.2%}")
    
    # Save
    save_model(model, vec)
    print("✅ Model saved to busted_ml/models/")

if __name__ == "__main__":
    train_and_save()