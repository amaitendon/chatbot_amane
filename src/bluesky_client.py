#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bluesky 投稿用クライアントモジュール

このモジュールは、AT Protocolを使用してBlueskyへの
ログインおよびテキスト投稿機能を提供します。
"""
import os
from atproto import Client, models, client_utils
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup
import io


class BlueskyClient:
    """Blueskyへの投稿を管理するクライアント"""
    
    def __init__(self):
        """
        BlueskyClientを初期化し、環境変数から認証情報を読み込む
        
        環境変数:
            BSKY_HANDLE (str): Blueskyのハンドル名（例: username.bsky.social）
            BSKY_PASSWORD (str): Blueskyのパスワード
        
        Raises:
            ValueError: BSKY_HANDLEまたはBSKY_PASSWORDが設定されていない場合
        """
        load_dotenv()
        self.handle = os.getenv('BSKY_HANDLE')
        self.password = os.getenv('BSKY_PASSWORD')
        self.client = None
        
        if not self.handle or not self.password:
            raise ValueError("BSKY_HANDLEとBSKY_PASSWORDが.envファイルに設定されていません")
    
    def login(self) -> bool:
        """
        Blueskyへログインする
        
        Returns:
            bool: ログインに成功した場合True、失敗した場合False
        """
        try:
            self.client = Client()
            self.client.login(self.handle, self.password)
            print(f"✓ ログイン成功: {self.handle}")
            return True
        except Exception as e:
            print(f"✗ ログイン失敗: {e}")
            return False
    
    def _fetch_ogp(self, url: str) -> dict:
        """
        URLからOGP情報を取得する
        
        Args:
            url (str): 情報を取得したいURL
            
        Returns:
            dict: {
                "title": str,
                "description": str,
                "image_data": bytes | None
            }
        """
        # デフォルトの戻り値
        result = {"title": url, "description": "", "image_data": None}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.7559.133 Safari/537.36"
        }
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:

                # HTMLの取得
                response = client.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
            
                # メタデータ取得用ヘルパー
                def get_meta(property_name):
                    tag = soup.find('meta', property=property_name) or soup.find('meta', attrs={'name': property_name})
                    return tag.get('content') if tag else None

                # タイトル、説明の取得
                result["title"] = get_meta('og:title') or soup.title.string if soup.title else url
                result["description"] = get_meta('og:description') or get_meta('description') or ""
                
                # 画像の取得
                image_url = get_meta('og:image')
                if image_url:
                    # 相対パスの場合は絶対パスに変換
                    if not image_url.startswith(('http://', 'https://')):
                        from urllib.parse import urljoin
                        image_url = urljoin(url, image_url)
                        
                    img_res = client.get(image_url)
                    if img_res.status_code == 200:
                        result["image_data"] = img_res.content

            return result

        except Exception as e:
            print(f"⚠ OGP取得失敗: {e}")
            return result

    def get_recent_posts(self, limit: int = 10) -> list:
        """
        自分の最近の投稿を取得する（重複チェック用）
        
        Args:
            limit (int): 取得する投稿数
            
        Returns:
            list: 投稿情報のリスト。各要素は以下の辞書:
                  {
                      "text": str,          # 投稿本文
                      "external_uri": str   # リンクカードのURI（なければNone）
                  }
        """
        if not self.client:
            print("✗ ログインしていません。先にlogin()を呼び出してください")
            return []

        try:
            # 自分のフィードを取得
            feed = self.client.get_author_feed(actor=self.handle, limit=limit)
            
            posts = []
            for item in feed.feed:
                post = item.post
                record = post.record
                
                # テキストの取得
                text = record.text if hasattr(record, 'text') else ""
                
                # 外部リンク（埋め込み）の取得
                external_uri = None
                if hasattr(record, 'embed') and record.embed:
                    # app.bsky.embed.external形式の場合
                    if hasattr(record.embed, 'external') and record.embed.external:
                         external_uri = record.embed.external.uri
                
                posts.append({
                    "text": text,
                    "external_uri": external_uri
                })
                
            return posts
            
        except Exception as e:
            print(f"✗ 投稿取得失敗: {e}")
            return []

    def post(self, text: str, url: str = None, append_url_flag: bool = True):
        """
        Blueskyに投稿する
        
        Args:
            text (str): 投稿したい文章
            url (str, optional): リンクカードとして表示したいURL
            append_url_flag (bool, optional): URLをテキストの末尾に追記するかどうか。デフォルトはTrue（追記する）。
        
        Returns:
            Response | None: 投稿に成功した場合はレスポンスオブジェクト、失敗した場合はNone
        """
        if not self.client:
            print("✗ ログインしていません。先にlogin()を呼び出してください")
            return None
        
        embed = None
        
        try:
            # URLが指定されている場合、リンクカードを作成
            if url:
                print(f"ℹ リンクカード情報を取得中: {url}")
                ogp = self._fetch_ogp(url)
                
                thumb_blob = None
                if ogp["image_data"]:
                    try:
                        upload = self.client.upload_blob(ogp["image_data"])
                        thumb_blob = upload.blob
                    except Exception as e:
                        print(f"⚠ 画像アップロード失敗: {e}")

                embed = models.AppBskyEmbedExternal.Main(
                    external=models.AppBskyEmbedExternal.External(
                        title=ogp["title"],
                        description=ogp["description"],
                        uri=url,
                        thumb=thumb_blob
                    )
                )

            # TextBuilderを使って投稿本文を構築
            tb = client_utils.TextBuilder()
            tb.text(text)
            
            # URL追記フラグが有効な場合、テキスト末尾にURLを追加（リンクとして）
            if append_url_flag and url:
                tb.text("\n\n")
                tb.link(url, url)

            # 投稿
            # send_postはTextBuilderオブジェクトを受け取れる
            print(f"ℹ 投稿中 (TextBuilderを使用): \n{text}")
            if append_url_flag and url:
                 print(f"{url}")
            print(f"ℹ 投稿中 (Embed): {embed}")
            
            response = self.client.send_post(tb, embed=embed)
            post_url = f"https://bsky.app/profile/{self.handle}/post/{response.uri.split('/')[-1]}"
            print(f"✓ 投稿成功!")
            print(f"  URL: {post_url}")
            return response
        except Exception as e:
            print(f"✗ 投稿失敗: {e}")
            return None
