# coding: utf-8
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import pandas as pd
from tqdm import tqdm
import pickle
import time
import random
import os

# スクレイピング対象のURLリストを生成
urls = [f"https://www.partzilla.com/search?ui=typeahead&filters=%5B%7B%22name%22%3A%22manufacturer%22%2C%22values%22%3A%5B%22SUZUKI%22%5D%7D%2C%7B%22name%22%3A%22sort%22%2C%22values%22%3A%5B%22score+desc%22%5D%7D%5D&pg={i}&pageSize=144" for i in range(1, 457)]

def main():
    """
    Partzillaからスズキのパーツ情報をスクレイピングし、CSVファイルに保存するメイン関数。
    チェックポイントからの再開機能、リトライ機能、エラーハンドリングを備える。
    """
    all_items = []
    failed_urls = []
    start_page = 0

    # チェックポイントファイルを探して、あれば途中から再開する
    # ファイル名を数字順でソートして最新のものを取得
    try:
        checkpoint_files = sorted([f for f in os.listdir('.') if f.startswith('suzuki_parts_checkpoint_') and f.endswith('.pkl')], key=lambda f: int(re.search(r'_(\d+)\.pkl$', f).group(1)))
        if checkpoint_files:
            latest_checkpoint = checkpoint_files[-1]
            print(f"最新のチェックポイントファイルが見つかりました: {latest_checkpoint}")
            with open(latest_checkpoint, 'rb') as f:
                all_items = pickle.load(f)
            # ファイル名からページ番号を抽出 (例: suzuki_parts_checkpoint_50.pkl -> 50)
            start_page = int(re.search(r'_(\d+)\.pkl$', latest_checkpoint).group(1))
            print(f"{start_page}ページまで完了済み。残りの処理を開始します。")
    except (IOError, pickle.UnpicklingError, AttributeError, ValueError, IndexError) as e:
        print(f"チェックポイントファイルの読み込みに失敗しました: {e}。最初から開始します。")
        all_items = []
        start_page = 0
    
    urls_to_scrape = urls[start_page:]
    if not urls_to_scrape:
        print("すべてのページのスクレイピングが完了しています。")
        # 完了している場合でも最終処理を行う
    else:
        print(f"スクレイピングを開始します (Page {start_page + 1} から {len(urls)} まで)")

    # WebDriverのオプションはループの外で定義
    options = Options()
    options.binary_location = "/usr/bin/chromium-browser"
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # ヘッドレスモードで実行したい場合は、次の行のコメントを解除してください
    # options.add_argument("--headless")

    if urls_to_scrape: # スクレイピングするURLがある場合のみ実行
        # tqdmの初期値を設定
        progress_bar = tqdm(urls_to_scrape, initial=start_page, total=len(urls), desc="Scraping pages")
        
        for i, url in enumerate(progress_bar):
            current_page_index = start_page + i
            progress_bar.set_description(f"Scraping page {current_page_index + 1}")

            for attempt in range(3): # 最大3回リトライ
                driver = None
                try:
                    service = Service("/usr/bin/chromedriver")
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.get(url)

                    wait = WebDriverWait(driver, 20)
                    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card")))
                    
                    cards = driver.find_elements(By.CLASS_NAME, "product-card")
                    items = []
                    for card in cards:
                        try:
                            name = card.find_element(By.CLASS_NAME, "product-name").text
                            type_element = card.find_element(By.CSS_SELECTOR, '[style="line-height: 1;"]')
                            type_number = type_element.text.replace("\n", " ") if type_element else "N/A"
                            price_text = card.find_element(By.CLASS_NAME, "sell-price").text
                            price = float(price_text.replace("$", "").replace(",", ""))
                            
                            items.append({
                                "name": name,
                                "type_number": type_number,
                                "price": price
                            })
                        except (NoSuchElementException, ValueError):
                            # カード内の要素欠損や価格変換エラーはスキップ
                            continue

                    all_items.extend(items)
                    time.sleep(random.uniform(1, 3)) # 成功時もサーバ負荷軽減のために待機
                    break # 成功したのでリトライを終了

                except TimeoutException:
                    print(f"\nURL: {url} - タイムアウト。リトライします... ({attempt + 1}/3)")
                    time.sleep(random.uniform(5, 15))
                    if attempt == 2:
                        print(f"\nURLの取得に3回失敗しました: {url}")
                        failed_urls.append(url)
                except Exception as e:
                    print(f"\n予期せぬエラーが発生しました (URL: {url}): {e}")
                    if attempt == 2:
                        print(f"\nURLの取得に3回失敗しました: {url}")
                        failed_urls.append(url)
                    time.sleep(10)
                finally:
                    if driver:
                        driver.quit()

            # 50ページごとに進捗を保存
            if (current_page_index + 1) % 50 == 0 and all_items:
                checkpoint_filename = f'suzuki_parts_checkpoint_{current_page_index + 1}.pkl'
                try:
                    with open(checkpoint_filename, 'wb') as f:
                        pickle.dump(all_items, f)
                    print(f"\n進捗を保存しました: {checkpoint_filename}")
                except IOError as e:
                    print(f"\nチェックポイントファイルの保存に失敗しました: {e}")

    print("\nスクレイピング完了。")
    
    if all_items:
        print("結果をCSVファイルに保存します...")
        result_df = pd.DataFrame(all_items)
        # 重複を除去
        # result_df.drop_duplicates(inplace=True)
        # print(f"最終的なアイテム数 (重複除去後): {len(result_df)}")
        print(f"最終的なアイテム数 : {len(result_df)}")
        print(f"重複しているアイテム数 : {result_df.duplicated().sum()}")
        
        try:
            result_df.to_csv("suzuki_parts.csv", index=False)
            print("suzuki_parts.csv に保存しました。")
        except IOError as e:
            print(f"CSVファイルの保存に失敗しました: {e}")
    else:
        print("取得できたアイテムがありませんでした。")

    if failed_urls:
        print("\n失敗したURLリスト:")
        for failed_url in failed_urls:
            print(failed_url)
        try:
            with open("failed_urls.txt", "w") as f:
                for url in failed_urls:
                    f.write(f"{url}\n")
            print("\n失敗したURLは failed_urls.txt に保存しました。")
        except IOError as e:
            print(f"失敗したURLリストの保存に失敗しました: {e}")

if __name__ == "__main__":
    main()
