# 📘 記事紹介AIボット

このリポジトリは、最新のAI関連記事を収集し、独自のキャラクター性を持ってBlueskyへ自動投稿するシステムのソースコードです。

---

## 🌟 プロジェクト概要

毎日指定した時間（JST 19:30など）に、RSSフィード（ZennのAIトピック）から記事を1件ピックアップし、Google Geminiを使用してキャラクターの口調に変換した上でBlueskyへ投稿します。

### 主な機能
* **自動ニュース収集:** `feedparser` を使用して Zenn の RSS フィードから 24 時間以内の記事を取得。
* **キャラクター紹介文生成:** Gemini を使用し、設定に基づいた親しみやすい投稿文を生成。
* **重複投稿防止:** Bluesky の過去の投稿を確認し、同じニュースを二度投稿しないように制御。
* **完全自動運用:** GitHub Actions を利用し、サーバーレスで毎日定時実行。

---

## 👤 キャラクター設定

環境変数や外部ファイルから、システムインストラクションとしてGeminiに渡す。

---

## 🛠️ 技術スタック

| カテゴリ | 使用技術 |
| :--- | :--- |
| **言語** | Python 3.14 |
| **プラットフォーム** | Bluesky |
| **AI (LLM)** | Google Gemini API |
| **自動化** | GitHub Actions |
| **主なライブラリ** | `atproto`, `google-genai`, `feedparser`, 等 |

---

## 📂 ディレクトリ構成

```text
ai-news-bot/
├── .github/workflows/
│   └── daily_post.yml  # 自動実行スケジュール設定
├── src/
│   ├── main.py             # メインロジック
│   ├── news_fetcher.py     # ニュース収集
│   ├── llm_generator.py    # Geminiによるテキスト生成
│   └── bluesky_client.py   # Bluesky API操作
├── requirements.txt        # 依存ライブラリ一覧
├── character_prompt.txt    # キャラ設定（ローカル用）
└── post_prompt.txt         # 投稿指示（ローカル用）