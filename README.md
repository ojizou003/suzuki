# suzuki

## 概要

このプロジェクトは、[Partzilla](https://www.partzilla.com/catalog/suzuki) からスズキのバイクパーツカタログ情報をスクレイピングするためのツールです。`selenium` を使用してデータを収集し、`pandas` を用いて整形・リスト化します。

主な処理は `dev.ipynb` のJupyter Notebookに実装されています。

## 特徴

- **Webスクレイピング**: `selenium` を利用して動的なウェブサイトから情報を取得します。
- **データ整形**: `pandas` を使って、収集したデータを扱いやすい形式に変換します。
- **対話的な開発**: Jupyter Notebook (`dev.ipynb`) を使うことで、処理を一つずつ確認しながら開発を進めることができます。

## インストール方法

### 1. 前提条件

- Python 3.12 以上
- Git

### 2. リポジトリのクローン

まず、このリポジトリをローカルマシンにクローンします。

```bash
git clone <リポジトリのURL>
cd suzuki
```

### 3. 依存関係のインストール

プロジェクトに必要なPythonライブラリをインストールします。

```bash
pip install pandas selenium tqdm ipykernel notebook nbconvert
```

### 4. Seleniumのセットアップ

このプロジェクトでは `selenium` を使用してブラウザを操作します。そのため、ウェブブラウザとそれに対応するWebDriverのインストールが必要です。

#### a. ウェブブラウザのインストール

[Google Chrome](https://www.google.com/chrome/) または [Chromium](https://www.chromium.org/getting-involved/download-chromium) をインストールしてください。

#### b. WebDriverのインストール

インストールしたブラウザのバージョンに合った [ChromeDriver](https://chromedriver.chromium.org/downloads) をダウンロードし、システムのパスが通ったディレクトリ（例: `/usr/local/bin`）に配置するか、プロジェクトフォルダ内に配置します。

#### c. `dev.ipynb` のパス設定

`dev.ipynb` ファイル内で、`selenium` がブラウザとWebDriverを見つけられるようにパスを設定している箇所があります。ご自身の環境に合わせて、これらのパスを修正してください。

```python
# dev.ipynb 内のコード例
options = Options()
options.binary_location = "/path/to/your/chrome-or-chromium"  # 例: "/usr/bin/chromium-browser"
service = Service("/path/to/your/chromedriver")          # 例: "/usr/bin/chromedriver"

driver = webdriver.Chrome(service=service, options=options)
```

## 使い方

このプロジェクトの処理は、`dev.ipynb`をPythonスクリプトに変換してから実行します。

### 1. スクリプトへの変換

まず、`jupyter nbconvert`コマンドを使い、`dev.ipynb`をPythonスクリプトに変換します。

```bash
jupyter nbconvert --to script dev.ipynb --output-dir . --output suzuki_scraper
```

このコマンドにより、`suzuki_scraper.py`という名前のPythonファイルがカレントディレクトリに生成されます。

### 2. スクリプトの実行

生成されたスクリプトを`python`コマンドで実行します。

```bash
python suzuki_scraper.py
```

## 注意事項

- Webスクレイピングは、対象サイトの利用規約に従って行ってください。短時間に大量のリクエストを送ると、サイトに負荷をかけ、アクセスがブロックされる可能性があります。
- サイトのHTML構造が変更されると、スクレイピングが機能しなくなることがあります。その場合は、コードのセレクタ等を修正する必要があります。

## 今後の展望

- 取得したデータのCSVやExcelファイルへの出力機能
- エラーハンドリングの強化
- 設定ファイルによるURLやパスの外部化

## ライセンス

このプロジェクトは [MIT License](LICENSE) のもとで公開されています。