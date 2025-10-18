import requests
from datetime import datetime, timedelta
import re

# Your NewsAPI key
API_KEY = "cf40c0a2aa0f404995ddf5dd85f71630"
BASE_URL = "https://newsapi.org/v2/everything"

def log(msg):
    """Simple logger"""
    print(f"[NewsAPI] {msg}")


def get_keywords(text):
    """Extract keywords from text"""
    stopwords = ['is', 'the', 'a', 'an', 'of', 'in', 'to', 'and', 'or', 'was', 
                 'are', 'has', 'have', 'for', 'on', 'at', 'by', 'with', 'be',
                 'shows', 'says', 'summit', 'ndtv']
    
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


def search_news(query_text):
    """
    Search for news using NewsAPI
    Returns list of verified sources with links
    """
    keywords = get_keywords(query_text)
    query = " ".join(keywords)
    
    log(f"Searching: {query}")
    log(f"User query: {query_text[:70]}...")
    
    # Calculate date range (last 30 days for better results)
    to_date = datetime.now()
    from_date = to_date - timedelta(days=30)
    
    # NewsAPI parameters
    params = {
        'q': query,
        'apiKey': API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt',
        'from': from_date.strftime('%Y-%m-%d'),
        'to': to_date.strftime('%Y-%m-%d'),
        'pageSize': 30  # Get more results
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            log(f"Error: Status {response.status_code}")
            return []
        
        data = response.json()
        
        if data.get('status') != 'ok':
            log(f"Error: {data.get('message', 'Unknown error')}")
            return []
        
        articles = data.get('articles', [])
        log(f"Found {len(articles)} articles from NewsAPI")
        
        # Filter and match articles
        verified = []
        
        for article in articles:
            title = article.get('title', '')
            source_name = article.get('source', {}).get('name', 'Unknown')
            url = article.get('url', '')
            
            if not title or not url:
                continue
            
            # Calculate similarity
            similarity = calculate_similarity(query_text, title)
            
            # Show ALL articles for debugging
            log(f"→ {source_name}: {similarity:.0%} - {title[:60]}...")
            
            # Include if 25%+ similar (very lenient for testing)
            if similarity > 0.25:
                log(f"✓ MATCHED!")
                verified.append({
                    'source': source_name,
                    'link': url,
                    'similarity': similarity,
                    'title': title
                })
        
        # Sort by similarity
        verified.sort(key=lambda x: x['similarity'], reverse=True)
        
        log(f"✅ Final: {len(verified)} verified articles")
        return verified
        
    except requests.exceptions.Timeout:
        log("Error: Request timeout")
        return []
    except Exception as e:
        log(f"Error: {str(e)}")
        return []


def check_domain(url):
    """
    Check if URL is from a trusted news domain
    Returns: 'trusted', 'fake', or 'unknown'
    """
    # Trusted domains
    trusted = [
        'bbc.com', 'bbc.co.uk',
        'ndtv.com',
        'timesofindia.indiatimes.com',
        'thehindu.com',
        'hindustantimes.com',
        'indianexpress.com',
        'reuters.com',
        'apnews.com',
        'cnn.com',
        'aljazeera.com',
        'theguardian.com',
        'nytimes.com'
    ]
    
    # Known fake news sites
    fake = [
        'fakeindianews.com',
        'fakingnews.com',
        'worldnewsdailyreport.com'
    ]
    
    url_lower = url.lower()
    
    for domain in trusted:
        if domain in url_lower:
            return 'trusted'
    
    for domain in fake:
        if domain in url_lower:
            return 'fake'
    
    return 'unknown'