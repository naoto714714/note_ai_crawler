"""
クローラーのテストモジュール
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.crawler import NoteCrawler
from src.utils import read_existing_urls, save_to_csv


class TestNoteCrawler:
    """
    NoteCrawlerクラスのテスト
    """

    def test_init(self):
        """
        初期化のテスト
        """
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # 初期化
            crawler = NoteCrawler(output_path=temp_path)

            # 検証
            assert crawler.output_path == temp_path
            assert isinstance(crawler.existing_urls, list)
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @patch("src.crawler.requests.get")
    def test_fetch_page(self, mock_get):
        """
        _fetch_pageメソッドのテスト
        """
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # クローラーの初期化
        crawler = NoteCrawler()

        # テスト
        response = crawler._fetch_page(1)

        # 検証
        assert response == mock_response
        mock_get.assert_called_once()

        # ページ2以降のテスト
        mock_get.reset_mock()
        crawler._fetch_page(2)

        # 検証（page=2パラメータが追加されていることを確認）
        args, kwargs = mock_get.call_args
        assert kwargs["params"].get("page") == 2

    @patch("src.crawler.requests.get")
    def test_fetch_page_error(self, mock_get):
        """
        _fetch_pageメソッドのエラー処理のテスト
        """
        # モックの設定（例外を発生させる）
        mock_get.side_effect = Exception("テスト例外")

        # クローラーの初期化
        crawler = NoteCrawler()

        # テスト
        response = crawler._fetch_page(1)

        # 検証（エラー時はNoneを返すことを確認）
        assert response is None

    def test_parse_articles(self):
        """
        _parse_articlesメソッドのテスト
        """
        # テスト用のHTML
        html = """
        <html>
        <body>
            <article>
                <h3>テスト記事1</h3>
                <a href="/user1/article1">リンク1</a>
            </article>
            <article>
                <h3>テスト記事2</h3>
                <a href="/user2/article2">リンク2</a>
                <div class="o-noteStatus">有料</div>
            </article>
        </body>
        </html>
        """

        # クローラーの初期化
        crawler = NoteCrawler()

        # テスト
        articles = crawler._parse_articles(html)

        # 検証
        assert len(articles) == 2
        assert articles[0]["title"] == "テスト記事1"
        assert articles[0]["url"] == "https://note.com/user1/article1"
        assert articles[0]["is_paid"] == "無料"

        assert articles[1]["title"] == "テスト記事2"
        assert articles[1]["url"] == "https://note.com/user2/article2"
        assert articles[1]["is_paid"] == "有料"


class TestUtils:
    """
    ユーティリティ関数のテスト
    """

    def test_save_to_csv(self):
        """
        save_to_csv関数のテスト
        """
        # テストデータ
        test_data = [
            {"title": "テスト1", "url": "https://example.com/1"},
            {"title": "テスト2", "url": "https://example.com/2"},
        ]

        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # CSVに保存
            save_to_csv(test_data, temp_path)

            # 保存されたデータを読み込み
            urls = read_existing_urls(temp_path)

            # 検証
            assert len(urls) == 2
            assert "https://example.com/1" in urls
            assert "https://example.com/2" in urls
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_read_existing_urls_empty(self):
        """
        read_existing_urls関数のテスト（ファイルが存在しない場合）
        """
        # 存在しないファイルパス
        non_existent_path = "non_existent_file.csv"

        # テスト
        urls = read_existing_urls(non_existent_path)

        # 検証
        assert urls == []
