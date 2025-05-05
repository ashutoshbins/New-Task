import requests

def fetch_news_articles(query, api_key, page_size=5):
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "apiKey": api_key, "pageSize": page_size, "language": "en"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [f"{a['title']}. {a.get('description', '')}" for a in articles]
    else:
        return []
