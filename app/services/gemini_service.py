import os

from dotenv import load_dotenv
from google import genai


# Load environment variables
load_dotenv()


# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Please add it to your .env file."
    )


# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def summarize_article(article):
    """
    Generate an AI summary for one news article.
    """

    title = article.get("title", "")
    description = article.get("description", "")
    category = article.get("category", "")
    source = article.get("source", "")

    prompt = f"""
You are TechMate AI, a technology news assistant.

Summarize this news article.

Category:
{category}

Source:
{source}

Title:
{title}

Description:
{description}

Rules:
- Write 2 to 4 sentences.
- Clearly explain what happened.
- Explain why it matters.
- Use simple language.
- Do not invent facts.
- Only use information provided above.
- Do not mention that you are an AI.
- Return only the summary.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text.strip()


def summarize_news_articles(articles):
    """
    Generate summaries for multiple articles.
    """

    summarized_articles = []

    for article in articles:

        try:
            summary = summarize_article(article)

        except Exception as error:
            print(
                f"\nGemini failed for article:"
                f"\n{article.get('title', 'Unknown')}"
            )

            print(f"Error: {error}")

            summary = "Summary unavailable."

        summarized_article = {
            **article,
            "ai_summary": summary,
        }

        summarized_articles.append(summarized_article)

    return summarized_articles


if __name__ == "__main__":

    from app.services.news_service import fetch_news

    print("Fetching real technology news...")

    articles = fetch_news()

    print(f"Found {len(articles)} articles.")

    summarized_articles = summarize_news_articles(articles)

    print("\n========== NEWS ==========")

    for article in summarized_articles:

        print("\n--------------------------")
        print("TITLE:", article["title"])
        print("CATEGORY:", article["category"])
        print("SOURCE:", article["source"])

        print("\nAI SUMMARY:")
        print(article["ai_summary"])