"""
ユーティリティ関数モジュール
"""

import csv
import os
from typing import Dict, List, Optional


def save_to_csv(
    data: List[Dict[str, str]],
    output_path: str = "data/articles.csv",
    mode: str = "w",
) -> None:
    """
    データをCSVファイルに保存する

    Args:
        data: 保存するデータのリスト。各要素は辞書形式で、キーがCSVのヘッダー、値がデータ
        output_path: 出力先のCSVファイルパス
        mode: ファイルオープンモード ('w'=上書き, 'a'=追記)
    """
    # 出力先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # データが空の場合は何もしない
    if not data:
        print("保存するデータがありません。")
        return

    # CSVファイルに書き込み
    file_exists = os.path.isfile(output_path) and os.path.getsize(output_path) > 0

    with open(output_path, mode, newline="", encoding="utf-8") as f:
        # 最初のデータの辞書のキーをヘッダーとして使用
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # ファイルが新規作成の場合、またはモードが'w'の場合はヘッダーを書き込む
        if mode == "w" or not file_exists:
            writer.writeheader()

        # データを書き込む
        writer.writerows(data)

    print(f"{len(data)}件のデータを{output_path}に保存しました。")


def read_existing_urls(csv_path: str) -> List[str]:
    """
    既存のCSVファイルからURLのリストを取得する

    Args:
        csv_path: CSVファイルのパス

    Returns:
        URLのリスト
    """
    urls = []

    # ファイルが存在しない場合は空のリストを返す
    if not os.path.isfile(csv_path):
        return urls

    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # URLというフィールドがあることを前提としている
            urls = [row.get("url", "") for row in reader if row.get("url")]
    except Exception as e:
        print(f"既存URLの読み込み中にエラーが発生しました: {e}")

    return urls
