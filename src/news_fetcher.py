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

def fetch_latest_ai_news():
    """
    ZennのAIトピックから24時間以内の最新ニュースを全て取得する。
    
    Returns:
        list: ニュース情報のリスト（各要素は dict: title, link, summary, published）
              24時間以内のニュースがない場合は空リスト []
    """
    print(f"Fetching RSS from {RSS_URL}...")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("No entries found in RSS feed.")
        return []
        
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
    
    count = len(recent_articles)
    if count == 0:
        print("No news found within the last 24 hours.")
        return []

    print(f"Found {count} recent articles.")
    return recent_articles

if __name__ == "__main__":
    # Test the function
    news_list = fetch_latest_ai_news()
    if news_list:
        print(f"Found {len(news_list)} articles:")
        for i, news in enumerate(news_list):
            print(f"[{i+1}] {news['title']}")
            print(f"    Link: {news['link']}")
            print(f"    Published: {news['published']}")
            print(f"    Summary: {news['summary']}")
    else:
        print("No news found.")