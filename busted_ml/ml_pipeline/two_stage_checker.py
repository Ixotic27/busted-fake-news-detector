from busted_ml.ml_pipeline.model import load_model
from busted_ml.ml_pipeline.preprocess import clean_text
from busted_ml.scraper.scraper import safe_get
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime
import re

# Load model once
model, vec = load_model()

# Trusted sources
TRUSTED_SOURCES = [
    "ndtv.com",
    "timesofindia.indiatimes.com",
    "thehindu.com",
    "hindustantimes.com",
    "indianexpress.com",
    "bbc.com",
    "reuters.com"
]

def log_debug(msg):
    """Debug logger"""
    print(f"[DEBUG] {msg}")

def stage1_ml_check(text):
    """Stage 1: ML Model Classification"""
    clean = clean_text(text)
    
    if not clean:
        return {"pred": "fake", "conf": 0.9, "reason": "Empty text"}
    
    vec_text = vec.transform([clean])
    pred = model.predict(vec_text)[0]
    conf = float(model.predict_proba(vec_text).max())
    
    log_debug(f"ML says: {pred.upper()} with {conf:.2%} confidence")
    
    return {"pred": pred, "conf": conf}

def stage2_web_verify(text):
    """Stage 2: Web Scraping Verification - PARALLEL"""
    keywords = extract_keywords(text)
    log_debug(f"Keywords: {keywords}")
    
    sources = []
    links = []
    
    def check_domain(domain):
        """Check single domain"""
        try:
            search_url = get_search_url(domain, keywords)
            log_debug(f"Checking: {domain}")
            
            resp = safe_get(search_url, timeout=3)
            
            if not resp.text:
                return None
            
            text_lower = resp.text.lower()
            matches = sum(1 for kw in keywords[:3] if kw in text_lower)
            
            if matches >= 2 or domain in text_lower:
                log_debug(f"✓ Found on {domain}")
                
                # Extract link
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if domain in href and 'http' in href:
                        clean_link = href.split('?')[0].split('&')[0]
                        return (domain, clean_link)
                
                return (domain, None)
            
            return None
            
        except Exception as e:
            log_debug(f"Error on {domain}: {str(e)}")
            return None
    
    # Parallel scraping (faster!)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(check_domain, d): d for d in TRUSTED_SOURCES}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                sources.append(result[0])
                if result[1]:
                    links.append(result[1])
    
    log_debug(f"Total sources found: {len(sources)}")
    
    return {
        "found": len(sources),
        "sources": sources,
        "links": links[:5]
    }

def get_search_url(domain, keywords):
    """Generate search URL for each domain"""
    query = "+".join(keywords[:3])
    
    # Direct site searches
    if "ndtv.com" in domain:
        return f"https://www.ndtv.com/search?q={query}"
    elif "timesofindia" in domain:
        return f"https://timesofindia.indiatimes.com/topic/{keywords[0]}"
    elif "thehindu.com" in domain:
        return f"https://www.thehindu.com/search/?q={query}"
    elif "hindustantimes" in domain:
        return f"https://www.hindustantimes.com/search?q={query}"
    elif "indianexpress" in domain:
        return f"https://indianexpress.com/?s={query}"
    else:
        # Fallback to Google site search
        return f"https://www.google.com/search?q=site:{domain}+{query}"

def extract_keywords(text):
    """Extract important words"""
    stop = ['is', 'the', 'a', 'an', 'of', 'in', 'to', 'and', 'or', 'was', 
            'are', 'has', 'have', 'for', 'on', 'at', 'by', 'with']
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if w not in stop and len(w) > 3]
    return keywords[:5]

def check_news_two_stage(text):
    """
    Main 2-Stage Checker - ALWAYS verify on web
    Stage 1: ML gives preliminary assessment
    Stage 2: Web verification is the final authority
    """
    
    # === STAGE 1: ML CHECK ===
    ml_result = stage1_ml_check(text)
    ml_pred = ml_result['pred']
    ml_conf = ml_result['conf']
    
    # === STAGE 2: ALWAYS WEB VERIFICATION ===
    log_debug("Starting web verification...")
    web_result = stage2_web_verify(text)
    found_count = web_result['found']
    sources = web_result['sources']
    links = web_result['links']
    
    # === SMART DECISION LOGIC ===
    
    # Case 1: Found on 2+ sources = REAL (Web overrides ML)
    if found_count >= 2:
        result = {
            "prediction": "VERIFIED REAL",
            "confidence": 0.90,
            "stage": "Web Verified (2+ sources)",
            "reason": f"Found on {found_count} trusted news sources",
            "ml_says": ml_pred,
            "sources": sources,
            "links": links
        }
    
    # Case 2: Found on 1 source
    elif found_count == 1:
        if ml_pred == "fake":
            result = {
                "prediction": "LIKELY REAL",
                "confidence": 0.70,
                "stage": "Web Override ML",
                "reason": "ML said fake, but found on trusted source. Verify manually.",
                "ml_says": ml_pred,
                "sources": sources,
                "links": links
            }
        else:
            result = {
                "prediction": "LIKELY REAL",
                "confidence": 0.80,
                "stage": "ML + Web Agree",
                "reason": "Found on 1 source and ML confirms",
                "ml_says": ml_pred,
                "sources": sources,
                "links": links
            }
    
    # Case 3: Not found anywhere
    else:
        if ml_pred == "fake" and ml_conf > 0.85:
            result = {
                "prediction": "LIKELY FAKE",
                "confidence": ml_conf,
                "stage": "ML + Web Agree",
                "reason": "ML detects fake patterns AND not verified anywhere",
                "ml_says": ml_pred,
                "sources": [],
                "links": []
            }
        elif ml_pred == "fake":
            result = {
                "prediction": "UNVERIFIED - POSSIBLY FAKE",
                "confidence": 0.65,
                "stage": "Cannot Verify",
                "reason": "Not found on trusted sources, ML suggests fake",
                "ml_says": ml_pred,
                "sources": [],
                "links": []
            }
        else:
            result = {
                "prediction": "UNVERIFIED",
                "confidence": 0.50,
                "stage": "Cannot Verify",
                "reason": "Not found on trusted sources. Cannot confirm.",
                "ml_says": ml_pred,
                "sources": [],
                "links": []
            }
    
    save_to_csv(text, result)
    return result

def save_to_csv(text, result):
    """Save results to CSV file"""
    csv_path = "busted_ml/data/check_results.csv"
    
    # Create file with headers if doesn't exist
    if not os.path.exists(csv_path):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "news_text", "prediction", 
                "confidence", "stage", "ml_says", 
                "sources", "links"
            ])
    
    # Append result
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            text[:200],  # First 200 chars
            result['prediction'],
            f"{result['confidence']:.2f}",
            result['stage'],
            result['ml_says'],
            ", ".join(result['sources']) if result['sources'] else "None",
            "; ".join(result['links']) if result['links'] else "None"
        ])