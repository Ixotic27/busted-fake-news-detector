import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_headlines(url="https://www.bbc.com/news"):
    """
    Fetches the headlines from BBC News (or any site with <h2> tags).
    Returns a list of strings.
    """

    # Send request (with a browser-like header so site doesn’t block us)
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")
   
    # Find all <h2> tags and get text

    articles=soup.find_all('a',href=True)
    results=[]

    for a in articles:
        title = a.get_text(strip=True)
        link = a['href']

        if title and "/news" in link:  # catch both relative and absolute
            if link.startswith("http"):
                full_link = link
            else:
                full_link = f"https://www.bbc.com{link}"
            results.append((title, full_link))

    # Return
    return results


if __name__ == "__main__":
    results = scrape_headlines()
    print("Top Headlines:")
    for i, (title, link) in enumerate(results, 1):
        print(f"{i}. {title} -> {link}")


df = pd.DataFrame(results, columns=["Headline", "Link"])

if os.path.exists("headlines.csv") and os.path.getsize("headlines.csv") > 0:
    old_df=pd.read_csv("headlines.csv")
    combined_df = pd.concat([old_df, df]).drop_duplicates().reset_index(drop=True)
else:
    combined_df=df
combined_df.to_csv("headlines.csv",index=False)


















