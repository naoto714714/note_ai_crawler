# note_ai_crawler

note.comの「AI」ハッシュタグが付けられた記事を新着順にクロールし、記事のURLを一覧として取得するクローラーです。取得したデータはCSV形式でローカルに保存されます。

## 機能

- note.comの「AI」ハッシュタグ付き記事を新着順にクロール
- 記事のタイトル、URL、日付などの情報をCSV形式で保存
- 重複を避けるための再クロール機能（オプション）

## 必要条件

- Python 3.13以上
- uvパッケージマネージャー

## インストール方法

```bash
# リポジトリをクローン
git clone https://github.com/naoto714714/note_ai_crawler.git
cd note_ai_crawler

# 依存パッケージのインストール
uv pip install -e .
```

## 使用方法

```bash
# 基本的な使い方
python -m src.crawler

# 保存先を指定する場合
python -m src.crawler --output path/to/output.csv
```

## ディレクトリ構成

```
note_ai_crawler/
├── .gitignore
├── pyproject.toml
├── README.md
├── data/
│   └── articles.csv       # クロール結果を保存するCSVファイル
├── src/
│   ├── crawler.py         # クロール処理メインロジック
│   └── utils.py           # ユーティリティ関数（CSV出力処理など）
└── tests/
    └── test_crawler.py    # テストコード
```

## ライセンス

MIT
