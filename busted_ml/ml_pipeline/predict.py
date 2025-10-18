import pandas as pd
from busted_ml.ml_pipeline.model import load_model
from busted_ml.ml_pipeline.preprocess import clean_text

def predict_csv(input_csv, output_csv):
    """
    Predict if scraped articles are fake/real
    Input: CSV with 'content' column from scraper
    Output: Same CSV + 'prediction' and 'confidence' columns
    """
    # Load model
    model, vec = load_model()
    
    # Read scraped data
    df = pd.read_csv(input_csv)
    
    # Clean content
    df['clean_content'] = df['content'].apply(clean_text)
    
    # Vectorize
    X = vec.transform(df['clean_content'])
    
    # Predict
    df['prediction'] = model.predict(X)
    df['confidence'] = model.predict_proba(X).max(axis=1)
    
    # Save results
    df.to_csv(output_csv, index=False)
    print(f"✅ Predictions saved to {output_csv}")
    
    # Show summary
    fake_count = (df['prediction'] == 'fake').sum()
    real_count = (df['prediction'] == 'real').sum()
    print(f"📊 Real: {real_count} | Fake: {fake_count}")
    
    return df

if __name__ == "__main__":
    predict_csv(
        "busted_ml/data/news_articles.csv",
        "busted_ml/data/predictions.csv"
    )