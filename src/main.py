import sys
from news_fetcher import fetch_latest_ai_news
from llm_generator import generate_post

def main():
    print("--- AI News Bot Started ---")
    
    # 1. 最新ニュースの取得
    print("Fetching latest AI news...")
    try:
        news = fetch_latest_ai_news()
    except Exception as e:
        print(f"Error fetching news: {e}")
        return

    # ニュースがなければ終了
    if not news:
        print("No news found within the last 24 hours.")
        return

    print(f"News Found: {news['title']}")
    print("-" * 30)

    # 2. 投稿文の生成
    print("Generating post with Gemini...")
    try:
        post_content = generate_post(news)
    except Exception as e:
        print(f"Error generating post: {e}")
        return

    print("-" * 30)
    print("Generated Post Content:")
    print(post_content)
    print("-" * 30)
    print("Original URL:", news['link'])
    print("--- Process Completed ---")

if __name__ == "__main__":
    main()
