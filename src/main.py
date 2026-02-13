#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import random
import time
import logging
from news_fetcher import fetch_latest_ai_news
from llm_generator import generate_post
from bluesky_client import BlueskyClient

MAX_AI_TEXT_CHARACTERS = 270   # blueskyは投稿文字数300文字まで。URLは24文字にカウントされる。余裕を持って設定する。

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    logging.info("--- AI News Bot Started ---")
    
    # 1. Login to Bluesky for duplicate check
    logging.info("Logging in to Bluesky...")
    bsky = BlueskyClient()
    recent_posts = []
    if bsky.login():
        recent_posts = bsky.get_recent_posts(limit=10)
    else:
        logging.error("Failed to login to Bluesky. Continuing without duplicate check.")

    # 2. Fetch News
    logging.info("Fetching daily AI news...")
    try:
        news_list = fetch_latest_ai_news()
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return

    # ニュースがなければ終了
    if not news_list:
        logging.info("No news found within the last 24 hours.")
        return


    # 3. ランダムな記事を選び、それが投稿済みの記事でないか確認する
    # 直近の投稿からリンクカードのURLを収集
    posted_urls = {post['external_uri'] for post in recent_posts if post.get('external_uri')}
    
    # ランダムな開始位置決定
    idx_start = random.randint(0, len(news_list) - 1)
    target_news = None
    
    # 重複していない記事を探す (全件ループ)
    for i in range(len(news_list)):
        current_idx = (idx_start + i) % len(news_list)
        candidate = news_list[current_idx]
        
        if candidate['link'] not in posted_urls:
            target_news = candidate
            if i > 0:
                logging.info(f"Duplicate found. Switched to next article: {target_news['title']}")
            break
            
    if not target_news:
        logging.info("All recent news articles have already been posted.")
        return
    

    # 4. Generate Content with Retry & Length Check
    post_content = ""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            logging.info(f"Generating post (Attempt {attempt+1})...")
            
            # If retrying due to length, add instruction
            append_instruction = None
            if attempt > 0 and len(post_content) > MAX_AI_TEXT_CHARACTERS:
                append_instruction = "\n全体で200文字以内となるように返信してください。SNSの文字数制限なので必ず守ってください。"
            
            post_content = generate_post(target_news, append_instruction)

            # 投稿文字数制限を超えそうか確認する
            if len(post_content) > MAX_AI_TEXT_CHARACTERS:
                if attempt < max_retries - 1:
                    logging.warning(f"Generated text too long ({len(post_content)} chars). Retrying...")
                    continue
                else:
                    logging.error("Failed to generate text within character limit after retries.")
                    # リトライしてそれでもダメならログ出力して終了
                    return
            
            # 正常なら次へ進む
            break 

        except Exception as e:
            logging.error(f"Error generating post: {e}")
            if attempt < max_retries - 1:
                sleep_time = 3 ** (attempt+1)
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logging.error("Max retries reached. Aborting.")
                return

    # 5. Dry Run Posting
    logging.info("-" * 30)
    logging.info("--- Generated Post Content ---")
    logging.info(post_content)
    logging.info(f"Character count: {len(post_content)}")
    logging.info("-" * 30)
    logging.info("Original URL: " + target_news['link'])
    
    # 投稿
    response = bsky.post(post_content, url=target_news['link'], append_url_flag=True)
    if response:
        logging.info("Successfully posted to Bluesky.")
    
    logging.info("--- Process Completed ---")

if __name__ == "__main__":
    main()
