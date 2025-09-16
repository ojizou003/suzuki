# suzuki — SUZUKI部品スクレイピング（Partzilla）

Partzilla 上の SUZUKI 部品一覧を Selenium でスクレイピングし、製品名・型番・価格を CSV に出力する最小構成プロジェクトです。

- 出力ファイル: `suzuki_parts.csv`
- 対象サイト: https://www.partzilla.com/
- 想定件数・所要時間（目安）: 約 65,000 アイテム（全 456 ページ）、約 3 時間弱（環境による）

注意: スクレイピング対象のサイトの規約・robots.txt・利用条件に従ってください。過度な負荷を避け、自己責任でご利用ください。

## 特徴（機能）

- 検索結果ページの `product-card` から以下を抽出
  - `name`: 製品名
  - `type_number`: 型番（`line-height: 1;` の要素から取得し、改行をスペースに変換）
  - `price`: 価格（`$` と `,` を除去して数値化）
- リトライと待機（タイムアウト時最大3回）
- チェックポイント保存（50ページごとに `suzuki_parts_checkpoint_XX.pkl`）と再開
- 取得結果の重複排除
- 失敗したURLの保存（`failed_urls.txt`）

## 前提条件

- Python 3.12 以上
- Chromium/Chrome と対応する ChromeDriver がインストール済み
  - 例: Chromium `/usr/bin/chromium-browser`、ChromeDriver `/usr/bin/chromedriver`
  - Selenium 4.x では Selenium Manager によりドライバ解決ができる場合があります（詳細は下記）。
- ネットワーク接続

依存関係は `pyproject.toml` と `uv.lock` で管理されています。

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
  - `uv run jupyter lab` または `uv run jupyter notebook`
- スクリプト実行
  - `uv run python scraping.py`

### 2) venv + pip を使う

```bash
python -m venv .venv
. .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -U pip
# uv がある場合はエクスポートしてインストール（シェルに合わせて調整）
uv export --no-hashes > requirements.txt && pip install -r requirements.txt
# もしくは主要パッケージを手動インストール
# pip install notebook selenium pandas tqdm ipykernel nbconvert
```

## 実行方法

このプロジェクトには 2 つの実行方法があります。用途に合わせて選択してください。

### A) Notebook（インタラクティブ実行）

1. Jupyter を起動し、`dev.ipynb` を開きます。
2. セルを上から順に実行します。
   - 最初のセルでライブラリをインポートします。
   - 2 番目のセルで対象ページの URL リストを生成します（既定は 1〜456 ページ）。
   - 3 番目のセルで各ページを巡回し、カード要素からデータを抽出します。
   - 4〜5 番目のセルで DataFrame を確認し、`suzuki_parts.csv` に保存します。
3. 実行完了後、リポジトリ直下に `suzuki_parts.csv` が生成されます。

所要時間の目安は通信環境・マシンスペックに依存します。長時間実行になり得るため、電源・スリープ設定に注意してください。

### B) スクリプト（バッチ実行）

`scraping.py` はチェックポイント/再開・リトライ・失敗URL保存などを含むバッチ実行用スクリプトです。

- 実行コマンド例
  - `python scraping.py`
  - `uv run python scraping.py`

- 実行時の挙動
  - 直近のチェックポイント（`suzuki_parts_checkpoint_*.pkl`）があればそれを読み込み、続きのページから再開します。
  - 50ページごとに最新の進捗をチェックポイントとして保存します。
  - 失敗したURLは `failed_urls.txt` に書き出します。
  - 最終的な結果は重複を除去して `suzuki_parts.csv` に保存します。

- ブラウザ/ドライバ設定（`scraping.py` 内の該当箇所）
  - 既定では以下のパスを使用します。環境に合わせて編集してください。
    - Chromium: `options.binary_location = "/usr/bin/chromium-browser"`
    - ChromeDriver: `Service("/usr/bin/chromedriver")`
  - Selenium Manager を使う場合のヒント
    - 上記2行（`binary_location` と `Service(...)`）の指定をコメントアウトし、`webdriver.Chrome(options=options)` のみで動作するか試してください。
  - ヘッドレス実行
    - `# options.add_argument("--headless")` のコメントを外す（新しい Chromium では `--headless=new` が安定な場合があります）。

## カスタマイズ

- ページ範囲の変更
  - `scraping.py` の `urls = [...] for i in range(1, 457)` を編集してください。
- 待機条件/タイムアウト
  - `WebDriverWait(driver, 20)` の秒数や、`EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))` を環境に応じて調整してください。
- アクセス間隔
  - 成功時も `time.sleep(random.uniform(1, 3))` で待機します。サイト負荷や安定度を見ながら調整してください。
- 出力形式/保存先
  - `result_df.to_csv("suzuki_parts.csv", index=False)` を編集することで TSV/Parquet などへ変更可能です。

## 出力スキーマ

- CSV 列: `name`, `type_number`, `price`
- 価格は数値（float）で保存されます。

## 再開（チェックポイント）について

- 50ページごとに `suzuki_parts_checkpoint_XX.pkl` が保存されます（XX は完了ページ数）。
- 次回起動時、最新のチェックポイントがあれば自動的に読み込まれ、続きから再開します。
- 不要になったチェックポイントは安全に削除できます（削除しても最終CSVがあればそのまま利用可能）。

## トラブルシューティング

- 要素が見つからない/タイムアウトする
  - タイムアウト値を延ばす、待機条件を安定なセレクタに変更する、スクロールや遅延を入れる。
- ChromeDriver とブラウザのバージョン不一致
  - バージョンを一致させるか、Selenium Manager を利用して自動解決を試す。
- ヘッドレスでは動く/動かない
  - ヘッドフルで一度動作確認し、差分をオプション（UA、ウィンドウサイズ、GPU 無効化など）で調整。
- アクセスブロック/レート制限
  - 待機時間を入れる、アクセス間隔を空ける、長時間連続実行を避ける。
- 書き込みエラー（CSV/チェックポイント）
  - 権限や空き容量、パスを確認。ネットワークドライブ上では一時的な I/O エラーに注意。

## プロジェクト構成

```
.
├── dev.ipynb          # スクレイピング実行用 Notebook
├── scraping.py        # バッチ実行用スクリプト（チェックポイント/再開対応）
├── pyproject.toml     # 依存関係/メタデータ
├── uv.lock            # 依存関係ロックファイル（uv）
├── .python-version    # 使用 Python バージョン
└── .gitignore
```

## 免責事項

本プロジェクトのコードは学習・検証用途を想定しています。スクレイピングは相手サイトの規約・法令の範囲内で行い、取得データの取り扱いには十分ご注意ください。サイト仕様変更により、コードが動作しなくなる可能性があります。
