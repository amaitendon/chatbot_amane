#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bluesky 投稿用クライアントモジュール

このモジュールは、AT Protocolを使用してBlueskyへの
ログインおよびテキスト投稿機能を提供します。
"""
import os
from atproto import Client
from dotenv import load_dotenv


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
    
    def post(self, text: str):
        """
        Blueskyにテキストを投稿する
        
        Args:
            text (str): 投稿したい文章
        
        Returns:
            Response | None: 投稿に成功した場合はレスポンスオブジェクト、失敗した場合はNone
        """
        if not self.client:
            print("✗ ログインしていません。先にlogin()を呼び出してください")
            return None
        
        try:
            response = self.client.send_post(text=text)
            post_url = f"https://bsky.app/profile/{self.handle}/post/{response.uri.split('/')[-1]}"
            print(f"✓ 投稿成功!")
            print(f"  URL: {post_url}")
            return response
        except Exception as e:
            print(f"✗ 投稿失敗: {e}")
            return None
