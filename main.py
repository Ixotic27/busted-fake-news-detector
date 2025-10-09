from busted_ml.ml_pipeline.preprocess import clean_text
from busted_ml.ml_pipeline.model import load_model

def main():
    # Load trained model
    model, vectorizer = load_model()

    # User input
    news = input("📰 Enter a news headline or article: ")

    # Preprocess + vectorize
    news_clean = clean_text(news)
    news_vec = vectorizer.transform([news_clean])

    # Predict
    prediction = model.predict(news_vec)[0]
    print(f"\n🔎 Prediction: {prediction}")

if __name__ == "__main__":
    main()
