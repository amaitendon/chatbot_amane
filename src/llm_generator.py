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


def load_character_prompt():
    """
    character_prompt.txt からキャラクタープロンプトを読み込む。
    """
    try:
        with open(PROJECT_ROOT / "character_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: character_prompt.txt not found. Using default prompt.")

        return "あなたは親切なAIアシスタントです。ニュースを要約してください。"

def generate_post(news_item):
    """
    ニュース記事を元に、Gemini APIを使用してSNS投稿文を生成する。
    
    Args:
        news_item (dict): タイトルと要約を含むニュース記事情報
        
    Returns:
        str: 生成された投稿文
    """
    if not API_KEY:
        return "Error: GEMINI_API_KEY not found in environment variables."

    try:
        character_prompt = load_character_prompt()
        
        user_prompt = f"""
        以下のAI関連記事を元に、SNS投稿文を作成してください。
        まず、記事の内容を120文字以内で要約してください。
        初心者にも分かりやすい表現を使って

        次に、記事に対する感想を120文字以内で述べてください。

        【制約事項】
        - 記事の内容に基づいた事実にのみ言及すること（ハルシネーション防止）
        - 入力されたニュースのURLは含めないでください（別途付与します）
 
        以下記事の内容です
        ---
        {news_item['title']}
        {news_item['summary']}
        ---
        """
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model=MODEL_NAME,
            config=genai.types.GenerateContentConfig(system_instruction=character_prompt),
            contents=user_prompt
        )
        
        return response.text
    except Exception as e:
        return f"Error generating content: {str(e)}"

if __name__ == "__main__":
    # Test the function with dummy data
    dummy_news = {
        "title": "AIがプログラミングを支援する新ツール発表",
        "summary": "XYZ社は、開発者の生産性を向上させる新しいAI搭載コーディングアシスタントを発表しました。"
    }
    print(load_character_prompt())
    # print(generate_post(dummy_news))
