# suzuki — SUZUKI部品スクレイピング（Partzilla）

このリポジトリは、Partzilla 上の SUZUKI 部品一覧を Selenium でスクレイピングし、製品名・型番・価格を CSV に出力するための最小構成プロジェクトです。実行は Jupyter Notebook（`dev.ipynb`）で行います。

- 出力ファイル: `suzuki_parts.csv`
- 対象サイト: https://www.partzilla.com/
- 想定件数・所要時間（目安）: 約 65,000 アイテム（全 456 ページ）、約 3 時間弱（環境による）

> 注意: スクレイピング対象のサイトの規約・robots.txt・利用条件に従ってください。過度な負荷を避け、自己責任でご利用ください。

## 取得するデータ

Notebook は各検索結果ページに表示される「product-card」から以下の情報を抽出します。

- `name`: 製品名
- `type_number`: 型番（画面上スタイル `line-height: 1;` の要素から取得し、改行をスペースに変換）
- `price`: 価格（`$` と `,` を除去して数値化）

## 前提条件

- Python 3.12 以上
- OS に Chromium/Chrome と対応する ChromeDriver がインストール済み
- ネットワーク接続

プロジェクトの Python 依存関係は `pyproject.toml` と `uv.lock` で管理されています。

主要依存関係（抜粋）:
- `selenium`
- `pandas`
- `tqdm`
- `notebook` / `nbconvert`

## セットアップ

以下のいずれかの方法で環境を準備してください。

### 1) uv を使う（推奨）

`uv` が未インストールの場合は公式ドキュメントに従ってセットアップしてください。

- 依存関係の同期
  - `uv sync`
- Jupyter の起動
  - `uv run jupyter lab` もしくは `uv run jupyter notebook`

### 2) venv + pip を使う

```bash
python -m venv .venv
. .venv/bin/activate    # Windows: .venv\\Scripts\\activate
pip install -U pip
pip install -r <(uv export --no-hashes)  # uv が無い場合は pyproject.toml を参照して手動でインストール
# もしくは pip install notebook selenium pandas tqdm ipykernel nbconvert
jupyter lab  # または jupyter notebook
```

## ブラウザ/ドライバの準備

Notebook では以下のパスを前提にしています。環境に合わせて `dev.ipynb` 内を編集してください。

- Chromium: `/usr/bin/chromium-browser`
- ChromeDriver: `/usr/bin/chromedriver`

ヒント:
- ディストリビューションによっては Chromium のパスが `/usr/bin/chromium` など異なる場合があります。
- Selenium 4 系では Selenium Manager によりパス指定を省略できる場合があります（`Service` や `binary_location` の指定を外す）。
- ヘッドレス実行は `options.add_argument("--headless")` のコメントアウトを外せば有効化できます（新しい Chromium では `--headless=new` が安定な場合があります）。

## 使い方（Notebook 実行）

1. Jupyter を起動し、`dev.ipynb` を開きます。
2. セルを上から順に実行します。
   - 最初のセルでライブラリをインポートします。
   - 2 番目のセルで対象ページの URL リストを生成します（既定は 1〜456 ページ）。
   - 3 番目のセルで各ページを巡回し、カード要素からデータを抽出します。
   - 4〜5 番目のセルで DataFrame を確認し、`suzuki_parts.csv` に保存します。
3. 実行完了後、リポジトリ直下に `suzuki_parts.csv` が生成されます。

所要時間の目安: 通信環境・マシンスペックに大きく依存します。長時間実行になる場合があるため、電源・スリープ設定にご注意ください。

## カスタマイズ

- ページ範囲の変更: `urls = [...] for i in range(1, 457)` の範囲を変更してください。
- ヘッドレス実行: `options.add_argument("--headless")`（または `--headless=new`）を有効化してください。
- 待機条件/タイムアウト: `WebDriverWait(driver, 10)` の秒数や待機条件（`EC.presence_of_element_located` など）を調整してください。
- 保存パス/形式の変更: `result_df.to_csv("suzuki_parts.csv", index=False)` を編集することで TSV/Parquet など別形式に変更可能です。

## トラブルシューティング

- 要素が見つからない/タイムアウトする
  - タイムアウト値を延ばす、待機条件を安定なセレクタに変更する、スクロールや遅延を入れる。
- ChromeDriver とブラウザのバージョン不一致
  - バージョンを一致させるか、Selenium Manager を利用して自動解決を試す。
- ヘッドレスでは動く/動かない
  - ヘッドフルで一度動作確認し、差分をオプション（UA、ウィンドウサイズ、GPU 無効化など）で調整。
- アクセスブロック/レート制限
  - 待機時間を入れる、アクセス間隔を空ける、長時間連続実行を避ける。

## プロジェクト構成

```
.
├── dev.ipynb          # スクレイピング実行用 Notebook
├── pyproject.toml     # 依存関係/メタデータ
├── uv.lock            # 依存関係ロックファイル（uv）
├── .python-version    # 使用 Python バージョン
└── .gitignore
```

## 免責事項

本プロジェクトのコードは学習・検証用途を想定しています。スクレイピングは相手サイトの規約・法令の範囲内で行い、取得データの取り扱いには十分ご注意ください。サイト仕様変更により、コードが動作しなくなる可能性があります。
