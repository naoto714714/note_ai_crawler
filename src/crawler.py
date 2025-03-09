"""
note.comのAIハッシュタグ付き記事をクロールするモジュール
"""

import argparse
import random
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from .utils import read_existing_urls, save_to_csv


class NoteCrawler:
    """
    note.comのクローラークラス
    """

    BASE_URL = "https://note.com/hashtag/AI"
    PARAMS = {"f": "new", "paid_only": "false"}
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    }

    def __init__(self, output_path: str = "data/articles.csv"):
        """
        初期化

        Args:
            output_path: 出力先のCSVファイルパス
        """
        self.output_path = output_path
        self.existing_urls = read_existing_urls(output_path)

    def crawl(self, max_pages: int = 5) -> List[Dict[str, str]]:
        """
        記事をクロールする

        Args:
            max_pages: クロールするページ数の上限

        Returns:
            クロールした記事データのリスト
        """
        all_articles = []
        page = 1

        while page <= max_pages:
            try:
                print(f"ページ{page}をクロール中...")

                # ページのHTMLを取得
                response = self._fetch_page(page)
                if not response:
                    break

                # 記事データを抽出
                articles = self._parse_articles(response.text)
                if not articles:
                    print("これ以上の記事が見つかりませんでした。")
                    break

                # 重複を除外して追加
                new_articles = [
                    a for a in articles if a.get("url") not in self.existing_urls
                ]
                all_articles.extend(new_articles)

                print(
                    f"ページ{page}から{len(new_articles)}件の新しい記事を取得しました。"
                )

                # 次のページへ
                page += 1

                # サーバーに負荷をかけないよう少し待機
                time.sleep(random.uniform(1.0, 3.0))

            except Exception as e:
                print(f"クロール中にエラーが発生しました: {e}")
                break

        return all_articles

    def _fetch_page(self, page: int) -> Optional[requests.Response]:
        """
        指定されたページのHTMLを取得する

        Args:
            page: ページ番号

        Returns:
            レスポンスオブジェクト、エラー時はNone
        """
        params = self.PARAMS.copy()
        if page > 1:
            params["page"] = page

        try:
            response = requests.get(
                self.BASE_URL, params=params, headers=self.HEADERS, timeout=30
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"ページ取得中にエラーが発生しました: {e}")
            return None

    def _parse_articles(self, html: str) -> List[Dict[str, str]]:
        """
        HTMLから記事データを抽出する

        Args:
            html: 解析するHTML文字列

        Returns:
            記事データのリスト
        """
        soup = BeautifulSoup(html, "lxml")
        articles = []

        # 記事のコンテナを探す
        article_containers = soup.select("article")

        for container in article_containers:
            try:
                # タイトル
                title_elem = container.select_one("h3")
                title = title_elem.text.strip() if title_elem else "タイトル不明"

                # リンク
                link_elem = container.select_one("a[href^='/']")
                url = f"https://note.com{link_elem['href']}" if link_elem else ""

                # 著者
                author_elem = container.select_one("a[href^='/']")
                author = author_elem.text.strip() if author_elem else "著者不明"

                # 日付（現在の実装では取得が難しい場合があるため、クロール日時を記録）
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 有料記事かどうか
                is_paid = "有料" if container.select_one(".o-noteStatus") else "無料"

                # 記事データを追加
                if url and url not in self.existing_urls:
                    articles.append(
                        {
                            "title": title,
                            "url": url,
                            "author": author,
                            "date": date,
                            "is_paid": is_paid,
                        }
                    )
            except Exception as e:
                print(f"記事データの抽出中にエラーが発生しました: {e}")
                continue

        return articles

    def save_articles(self, articles: List[Dict[str, str]]) -> None:
        """
        記事データをCSVに保存する

        Args:
            articles: 保存する記事データのリスト
        """
        save_to_csv(articles, self.output_path)
        # 既存URLリストを更新
        self.existing_urls.extend([a.get("url", "") for a in articles])


def main():
    """
    メイン関数
    """
    parser = argparse.ArgumentParser(
        description="note.comのAIハッシュタグ付き記事をクロールするツール"
    )
    parser.add_argument(
        "--output", default="data/articles.csv", help="出力先のCSVファイルパス"
    )
    parser.add_argument(
        "--pages", type=int, default=5, help="クロールするページ数の上限"
    )
    args = parser.parse_args()

    # クローラーの初期化と実行
    crawler = NoteCrawler(output_path=args.output)
    articles = crawler.crawl(max_pages=args.pages)

    # 結果の保存
    if articles:
        crawler.save_articles(articles)
        print(f"合計{len(articles)}件の記事を取得しました。")
    else:
        print("新しい記事は見つかりませんでした。")


if __name__ == "__main__":
    main()
