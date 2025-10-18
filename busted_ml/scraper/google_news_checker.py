import requests
import re
from bs4 import BeautifulSoup

def log(msg):
    """Simple logger"""
    print(f"[GoogleNews] {msg}")


def get_keywords(text):
    """Extract keywords from text"""
    stopwords = ['is', 'the', 'a', 'an', 'of', 'in', 'to', 'and', 'or', 'was', 
                 'are', 'has', 'have', 'for', 'on', 'at', 'by', 'with', 'be',
                 'shows', 'says', 'summit', 'tells', 'after']
    
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if w not in stopwords and len(w) > 3]
    
    return keywords[:5]


def calculate_similarity(text1, text2):
    """Calculate text similarity (0.0 to 1.0)"""
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    stopwords = {'is', 'the', 'a', 'an', 'of', 'in', 'to', 'and', 'or', 'was', 
                 'are', 'has', 'have', 'for', 'on', 'at', 'by', 'with', 'be'}
    
    words1 = words1 - stopwords
    words2 = words2 - stopwords
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def search_google_news(query_text):
    """
    Search Google News RSS feed
    Free, no API key needed, great for Indian news!
    """
    keywords = get_keywords(query_text)
    query = "+".join(keywords)
    
    log(f"Keywords: {keywords}")
    log(f"Searching Google News for: {query}")
    
    # Google News RSS URL (India edition)
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        
        log(f"Fetching from Google News RSS...")
        response = requests.get(rss_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            log(f"❌ Error: Status {response.status_code}")
            return []
        
        # Parse RSS feed (XML format)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        log(f"✓ Found {len(items)} articles from Google News")
        
        verified = []
        
        # Check each article
        for item in items[:25]:  # Check first 25 articles
            title_tag = item.find('title')
            link_tag = item.find('link')
            source_tag = item.find('source')
            
            if not title_tag or not link_tag:
                continue
            
            title = title_tag.get_text()
            url = link_tag.get_text()
            source_name = source_tag.get_text() if source_tag else "Unknown Source"
            
            # Calculate similarity
            similarity = calculate_similarity(query_text, title)
            
            log(f"→ {source_name}: {similarity:.0%} - {title[:60]}...")
            
            # Include if 30%+ similar
            if similarity > 0.30:
                log(f"✓ MATCHED! Adding to verified list")
                verified.append({
                    'source': source_name,
                    'link': url,
                    'similarity': similarity,
                    'title': title
                })
        
        # Sort by similarity (best matches first)
        verified.sort(key=lambda x: x['similarity'], reverse=True)
        
        log(f"✅ Final Result: {len(verified)} verified articles")
        
        return verified
        
    except requests.exceptions.Timeout:
        log("❌ Error: Request timeout")
        return []
    except Exception as e:
        log(f"❌ Error: {str(e)}")
        return []


def check_domain(url):
    """
    Check if URL is from a trusted news domain
    Returns: 'trusted', 'fake', or 'unknown'
    """
    # Trusted Indian & International news sources
    trusted = [
        'bbc.com', 'bbc.co.uk',
        'ndtv.com',
        'timesofindia.indiatimes.com',
        'thehindu.com',
        'hindustantimes.com',
        'indianexpress.com',
        'reuters.com',
        'apnews.com', 'ap.org',
        'cnn.com',
        'aljazeera.com',
        'theguardian.com',
        'nytimes.com',
        'news18.com',
        'financialexpress.com',
        'business-standard.com',
        'economictimes.indiatimes.com'
    ]
    
    # Known fake news sites
    fake = [
        'fakeindianews.com',
        'fakingnews.com',
        'worldnewsdailyreport.com',
        'huzlers.com',
        'theonion.com'
    ]
    
    url_lower = url.lower()
    
    # Check if trusted
    for domain in trusted:
        if domain in url_lower:
            return 'trusted'
    
    # Check if fake
    for domain in fake:
        if domain in url_lower:
            return 'fake'
    
    return 'unknown'