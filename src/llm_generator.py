#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI投稿生成モジュール

Gemini APIを使用して、取得したニュース記事を元に
キャラクター設定に基づいたSNS投稿文を生成する機能を提供します。
"""
import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")


def generate_post(news_item, append_instruction=None):
    """
    記事タイトルとサマリーを元に、Gemini APIを使用して、SNS投稿文を生成する。
    
    Args:
        news_item (dict): タイトルと要約を含むニュース記事情報
            'title' と 'summary' をキーに持つ必要あり
        append_instruction (str, optional): 末尾に追加する指示（リトライ時の追加指示用）
    Returns:
        str: 生成された投稿文

    Raises:
        ValueError: APIキーが環境変数に設定されていない場合に発生します。
        google.genai.errors.ClientError: プロンプトが長すぎる、または無効な引数が渡された場合など、
            クライアント側の不備でAPIリクエストが失敗した際に発生します。
        google.genai.errors.ServerError: Google側のサーバーエラーや一時的な過負荷（500系エラー）
            が発生した際に発生します。
        ValueError: 安全フィルターによってコンテンツがブロックされ、テキストが空の場合に発生します。
        FileNotFoundError: character_prompt.txt または post_prompt.txt が見つからない場合に発生します。
    """
    if not API_KEY:
        raise ValueError("APIキーが設定されていません！オーナー、API使用料を出し惜しみしないでくださいね！")

    character_prompt = Path(PROJECT_ROOT / "character_prompt.txt").read_text(encoding="utf-8")
    user_prompt = Path(PROJECT_ROOT / "post_prompt.txt").read_text(encoding="utf-8") + f"""
    以下記事の内容です
    ---
    {news_item['title']}
    {news_item['summary']}
    ---
    以上記事の内容でした。それではSNSに投稿する内容を作成してください。
    """
    
    if append_instruction:
        user_prompt += f"\n\n{append_instruction}"
    
    # 内部でtry-exceptせず、エラーは呼び出し元へ投げる
    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model=MODEL_NAME,
        config=genai.types.GenerateContentConfig(system_instruction=character_prompt),
        contents=user_prompt
    )
    
    return response.text

if __name__ == "__main__":
    # Test the function with dummy data
    dummy_news = {
        "title": "AIがプログラミングを支援する新ツール発表",
        "summary": "XYZ社は、開発者の生産性を向上させる新しいAI搭載コーディングアシスタントを発表しました。"
    }
    # print(load_character_prompt())
    # print(generate_post(dummy_news))
