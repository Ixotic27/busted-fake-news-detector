from busted_ml.ml_pipeline.model import load_model
from busted_ml.ml_pipeline.preprocess import clean_text
from busted_ml.scraper.google_news_checker import search_google_news, check_domain
import csv
import os
from datetime import datetime

# Load ML model once
model, vec = load_model()

def log(msg):
    """Simple logger"""
    print(f"[CHECKER] {msg}")


# ========== STAGE 1: ML MODEL ==========

def ml_predict(text):
    """Check if text looks fake using ML model"""
    clean = clean_text(text)
    
    if not clean:
        return {"pred": "fake", "conf": 0.9}
    
    vec_text = vec.transform([clean])
    pred = model.predict(vec_text)[0]
    conf = float(model.predict_proba(vec_text).max())
    
    log(f"ML: {pred.upper()} ({conf:.0%})")
    return {"pred": pred, "conf": conf}


# ========== MAIN CHECKER ==========

def check_news(text, url=None):
    """
    Two-stage fact checker with Google News:
    1. If URL provided → Check domain
    2. ML model check
    3. Google News verification
    """
    
    log("="*50)
    log("Starting fact check...")
    
    # === STAGE 1: URL Domain Check (if provided) ===
    if url:
        domain_status = check_domain(url)
        log(f"Domain check: {domain_status}")
        
        if domain_status == 'trusted':
            log("✓ URL from trusted domain - VERIFIED REAL")
            return {
                "prediction": "VERIFIED REAL",
                "confidence": 0.95,
                "stage": "Trusted Domain",
                "reason": "URL is from a verified trusted news source",
                "ml_says": "N/A",
                "verified_sources": [{
                    "source": "Trusted Domain",
                    "link": url,
                    "similarity": 1.0
                }]
            }
        
        elif domain_status == 'fake':
            log("✗ URL from fake domain - FAKE NEWS")
            return {
                "prediction": "FAKE",
                "confidence": 0.95,
                "stage": "Known Fake Domain",
                "reason": "URL is from a known fake news website",
                "ml_says": "N/A",
                "verified_sources": []
            }
    
    # === STAGE 2: ML Check ===
    ml = ml_predict(text)
    
    # === STAGE 3: Google News Verification ===
    log("Searching Google News...")
    verified = search_google_news(text)
    count = len(verified)
    
    log(f"Verification complete: {count} sources found")
    
    # === DECISION LOGIC ===
    
    if count >= 3:
        result = {
            "prediction": "VERIFIED REAL",
            "confidence": 0.95,
            "stage": "Google News Verified",
            "reason": f"Found on {count} trusted news sources",
            "ml_says": ml['pred'],
            "verified_sources": verified[:5]  # Top 5 matches
        }
    
    elif count >= 2:
        result = {
            "prediction": "VERIFIED REAL",
            "confidence": 0.90,
            "stage": "Google News Verified",
            "reason": f"Found on {count} trusted sources",
            "ml_says": ml['pred'],
            "verified_sources": verified
        }
    
    elif count == 1:
        result = {
            "prediction": "LIKELY REAL",
            "confidence": 0.75,
            "stage": "Single Source",
            "reason": "Found on 1 trusted source",
            "ml_says": ml['pred'],
            "verified_sources": verified
        }
    
    else:  # count == 0
        if ml['pred'] == "fake" and ml['conf'] > 0.85:
            result = {
                "prediction": "LIKELY FAKE",
                "confidence": ml['conf'],
                "stage": "ML + No Sources",
                "reason": "ML detects fake patterns AND not found on any news source",
                "ml_says": ml['pred'],
                "verified_sources": []
            }
        else:
            result = {
                "prediction": "UNVERIFIED",
                "confidence": 0.50,
                "stage": "Cannot Verify",
                "reason": "Not found on any trusted news source",
                "ml_says": ml['pred'],
                "verified_sources": []
            }
    
    save_result(text, result)
    log("="*50)
    return result


# ========== SAVE TO CSV ==========

def save_result(text, result):
    """Save results to CSV"""
    csv_file = "busted_ml/data/check_results.csv"
    
    if not os.path.exists(csv_file):
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "news_text", "prediction", 
                       "confidence", "stage", "ml_says", "verified_sources"])
    
    verified = result.get('verified_sources', [])
    sources_str = "; ".join([
        f"{v['source']} ({v.get('similarity', 0):.0%}): {v['link']}" 
        for v in verified
    ]) or "None"
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            text[:150],
            result['prediction'],
            f"{result['confidence']:.2f}",
            result['stage'],
            result['ml_says'],
            sources_str
        ])