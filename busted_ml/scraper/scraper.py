try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    requests = None
    REQUESTS_AVAILABLE = False

from bs4 import BeautifulSoup
import csv
import time
import urllib.request
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def safe_get(url, headers=None, timeout=10):
    """Get webpage content - tries requests, falls back to urllib"""
    if REQUESTS_AVAILABLE:
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except Exception:
            pass
    
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            charset = None
            try:
                charset = resp.info().get_content_charset()
            except:
                pass
            
            class Resp:
                def __init__(self, content, enc):
                    self.txt = content.decode(enc or "utf-8", errors="replace")
                @property
                def text(self):
                    return self.txt
            
            return Resp(data, charset)
    except:
        class EmptyResp:
            text = ""
        return EmptyResp()

def scrape_article(url, src_name):
    """Scrape single article from URL"""
    try:
        resp = safe_get(url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Get title
        title = ""
        for tag in ["h1", "h2", "title"]:
            t = soup.find(tag)
            if t:
                title = t.text.strip()
                break
        
        # Get content from all paragraphs
        paragraphs = soup.find_all("p")
        content = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])
        
        return {
            "source": src_name,
            "title": title or "N/A",
            "link": url,
            "content": content or "N/A"
        }
    except Exception as e:
        return {
            "source": src_name,
            "title": "ERROR",
            "link": url,
            "content": f"Failed to scrape: {str(e)}"
        }

def scrape_from_csv(input_csv, output_csv):
    """
    Read URLs from CSV and scrape them.
    Input CSV should have columns: source, url
    """
    articles = []
    
    # Read input CSV
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        urls = list(reader)
    
    print(f"📰 Found {len(urls)} URLs to scrape...")
    
    # Scrape each URL
    for i, row in enumerate(urls, 1):
        src = row.get("source", "Unknown")
        url = row.get("url", "").strip()
        
        if not url:
            continue
        
        print(f"[{i}/{len(urls)}] Scraping {src}...")
        article = scrape_article(url, src)
        articles.append(article)
        time.sleep(1)  # Be polite to servers
    
    # Save to output CSV
    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "title", "link", "content"])
        writer.writeheader()
        writer.writerows(articles)
    
    print(f"✅ Scraped {len(articles)} articles → {output_csv}")
    return articles

# Run if executed directly
if __name__ == "__main__":
    scrape_from_csv("data/news_urls.csv", "data/news_articles.csv")