#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ニュース取得モジュール

このモジュールは、指定されたRSSフィード（ZennのAIトピック）から
最新のAI関連ニュースを取得し、フィルタリングして返却する機能を提供します。
"""
import feedparser
from datetime import datetime, timedelta, timezone
import time
from email.utils import parsedate_to_datetime
import sys


RSS_URL = "https://zenn.dev/topics/ai/feed"

def fetch_latest_ai_news(index=0):
    """
    ZennのAIトピックから24時間以内の最新ニュースを取得する。
    
    Args:
        index (int): 取得するニュースのインデックス（0が最新）。
                     記事数を超える場合は剰余を取って選択する。
    
    Returns:
        dict: ニュースの情報（title, link, summary, published）
        None: 24時間以内のニュースがない場合
    """
    print(f"Fetching RSS from {RSS_URL}...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("No entries found in RSS feed.")
        return None
        
    # 現在時刻（UTC）
    now = datetime.now(timezone.utc)
    cutoff_time = now - timedelta(hours=24)
    
    # 24時間以内の記事を全て取得
    recent_articles = []
    for entry in feed.entries:
        # published_parsed は struct_time なので datetime に変換する
        # feedparserはUTCでパースする
        if hasattr(entry, 'published_parsed'):
            published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            
            # 24時間以内かチェック
            if published_time >= cutoff_time:
                recent_articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.summary if hasattr(entry, 'summary') else "",
                    "published": published_time.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    if not recent_articles:
        print("No news found within the last 24 hours.")
        return None

    # 記事数
    count = len(recent_articles)
    print(f"Found {count} recent articles.")

    # インデックスの正規化（剰余）
    target_index = index % count
    print(f"Selected index: {target_index} (requested: {index})")

    return recent_articles[target_index]

if __name__ == "__main__":
    # コマンドライン引数からインデックスを取得
    target_idx = 0
    if len(sys.argv) > 1:
        try:
            target_idx = int(sys.argv[1])
        except ValueError:
            print("Invalid index provided. Using default (0).")

    # Test the function
    news = fetch_latest_ai_news(target_idx)
    if news:
        print("Latest News Found:")
        print(f"Title: {news['title']}")
        print(f"Link: {news['link']}")
        print(f"Published: {news['published']}")
        print(f"Summary: {news['summary']}")
    else:
        print("No news found.")