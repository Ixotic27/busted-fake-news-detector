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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}


def safe_get(url, headers=None, timeout=10):
    """
    Return an object with a .text attribute similar to requests.Response.
    Tries requests if available, otherwise falls back to urllib.
    """
    if REQUESTS_AVAILABLE:
        try:
            return requests.get(url, headers=headers, timeout=timeout)
        except Exception:
            pass

    # urllib fallback
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            # try to get charset from headers
            charset = None
            try:
                info = resp.info()
                charset = info.get_content_charset()
            except Exception:
                charset = None

            class Resp:
                def __init__(self, content, charset):
                    self._content = content
                    self._charset = charset

                @property
                def text(self):
                    enc = self._charset or "utf-8"
                    try:
                        return self._content.decode(enc, errors="replace")
                    except Exception:
                        return self._content.decode("utf-8", errors="replace")

            return Resp(data, charset)
    except Exception:
        class EmptyResp:
            text = ""
        return EmptyResp()

# Function to scrape NDTV
def scrape_ndtv():
    url = "https://www.ndtv.com/latest"
    response = safe_get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    for item in soup.find_all("div", class_="news_Itm-cont"):
        title_tag = item.find("h2", class_="newsHdng")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link = title_tag.find("a")["href"]

        try:
            article_page = safe_get(link, headers=HEADERS)
            article_soup = BeautifulSoup(article_page.text, "html.parser")
            content = " ".join([p.text for p in article_soup.find_all("p")])
        except:
            content = "N/A"

        articles.append({"source": "NDTV", "title": title, "link": link, "content": content})
        time.sleep(1)
    return articles

# Function to scrape Times of India
def scrape_toi():
    url = "https://timesofindia.indiatimes.com/briefs"
    response = safe_get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    for item in soup.find_all("div", class_="brief_box"):
        title_tag = item.find("h2")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link_tag = title_tag.find("a")
        link = "https://timesofindia.indiatimes.com" + link_tag["href"] if link_tag else "N/A"

        try:
            article_page = safe_get(link, headers=HEADERS)
            article_soup = BeautifulSoup(article_page.text, "html.parser")
            content = " ".join([p.text for p in article_soup.find_all("p")])
        except:
            content = "N/A"

        articles.append({"source": "Times of India", "title": title, "link": link, "content": content})
        time.sleep(1)
    return articles

# Function to scrape Hindustan Times
def scrape_ht():
    url = "https://www.hindustantimes.com/latest-news"
    response = safe_get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = []
    for item in soup.find_all("div", class_="storyCard"):
        title_tag = item.find("h3")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        link_tag = title_tag.find("a")
        link = link_tag["href"] if link_tag else "N/A"

        try:
            article_page = safe_get(link, headers=HEADERS)
            article_soup = BeautifulSoup(article_page.text, "html.parser")
            content = " ".join([p.text for p in article_soup.find_all("p")])
        except:
            content = "N/A"

        articles.append({"source": "Hindustan Times", "title": title, "link": link, "content": content})
        time.sleep(1)
    return articles

# Main scraping
all_articles = []
all_articles.extend(scrape_ndtv())
all_articles.extend(scrape_toi())
all_articles.extend(scrape_ht())

# Save to CSV
keys = ["source", "title", "link", "content"]
with open("data/news_articles.csv", "w", newline="", encoding="utf-8") as f:
    dict_writer = csv.DictWriter(f, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(all_articles)

print(f"✅ Scraped {len(all_articles)} articles. Saved to data/news_articles.csv")













