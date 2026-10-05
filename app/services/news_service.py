import feedparser


NEWS_FEEDS = {
    "AI": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "Programming": "https://realpython.com/atom.xml",
    "Cybersecurity": "https://feeds.feedburner.com/TheHackersNews",
}


def fetch_news():
    articles = []

    for category, feed_url in NEWS_FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            article = {
                "title": entry.get("title", ""),
                "description": entry.get("summary", ""),
                "source": feed.feed.get("title", ""),
                "url": entry.get("link", ""),
                "category": category,
                "published": entry.get("published", ""),
            }

            articles.append(article)

    return articles


if __name__ == "__main__":
    news = fetch_news()

    print(f"Found {len(news)} articles.")

    for article in news:
        print("\n-----------------------------")
        print("TITLE:", article["title"])
        print("CATEGORY:", article["category"])
        print("SOURCE:", article["source"])
        print("PUBLISHED:", article["published"])
        print("URL:", article["url"])