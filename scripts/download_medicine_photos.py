"""
藥物圖片下載腳本
從 medicine_data.csv 讀取藥物資料並下載外觀圖片
"""

import csv
import os
import sys
import requests
from pathlib import Path
import time
from urllib.parse import urlparse

# 設定 stdout 編碼為 UTF-8
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 設定路徑
BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "medicine_data.csv"
PHOTOS_DIR = BASE_DIR / "medicine_photos"

# 確保圖片資料夾存在
PHOTOS_DIR.mkdir(exist_ok=True)


def sanitize_filename(filename):
    """清理檔案名稱，移除不合法字元"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename


def get_image_extension(url):
    """從 URL 或 Content-Type 取得圖片副檔名"""
    try:
        # 先嘗試從 URL 取得
        parsed = urlparse(url)
        path = parsed.path
        if "." in path:
            ext = path.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png", "gif", "bmp"]:
                return f".{ext}"

        # 如果從 URL 取得不到，預設使用 .jpg
        return ".jpg"
    except:
        return ".jpg"


def download_image(url, save_path, max_retries=3):
    """下載圖片，包含重試機制"""
    for attempt in range(max_retries):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            with open(save_path, "wb") as f:
                f.write(response.content)

            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  重試 {attempt + 1}/{max_retries}...")
                time.sleep(2)
            else:
                print(f"  下載失敗: {str(e)}")
                return False

    return False


def process_csv_and_download():
    """處理 CSV 檔案並下載圖片"""

    if not CSV_FILE.exists():
        print(f"錯誤: 找不到 CSV 檔案 {CSV_FILE}")
        return

    print(f"開始讀取 CSV 檔案: {CSV_FILE}")
    print(f"圖片將儲存至: {PHOTOS_DIR}")
    print("-" * 60)

    total_count = 0
    success_count = 0
    failed_count = 0
    skipped_count = 0

    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        # 檢查欄位名稱
        fieldnames = reader.fieldnames
        print(f"CSV 欄位: {fieldnames}\n")

        for row_num, row in enumerate(reader, start=2):
            license_number = row.get("許可證字號", "").strip()
            drug_name = row.get("中文品名", "").strip()
            image_urls = row.get("外觀圖檔連結", "").strip()

            if not license_number or not image_urls:
                continue

            # 清理許可證字號作為檔案名稱
            clean_license = sanitize_filename(license_number)

            # 分割多個圖片 URL（用 ;;; 分隔）
            urls = [url.strip() for url in image_urls.split(";;;") if url.strip()]

            print(f"\n[{row_num}] 處理: {drug_name} ({license_number})")
            print(f"  找到 {len(urls)} 個圖片連結")

            for idx, url in enumerate(urls):
                total_count += 1

                # 決定檔案名稱
                if len(urls) == 1:
                    filename = f"{clean_license}.jpg"
                else:
                    filename = f"{clean_license}_{idx + 1}.jpg"

                save_path = PHOTOS_DIR / filename

                # 檢查檔案是否已存在
                if save_path.exists():
                    print(f"  [{idx + 1}] 已存在，跳過: {filename}")
                    skipped_count += 1
                    continue

                print(f"  [{idx + 1}] 下載中: {filename}")

                if download_image(url, save_path):
                    success_count += 1
                    print(f"  [{idx + 1}] ✓ 下載成功")
                else:
                    failed_count += 1
                    print(f"  [{idx + 1}] ✗ 下載失敗")

                # 避免請求過於頻繁
                time.sleep(0.5)

    print("\n" + "=" * 60)
    print("下載完成!")
    print(f"總共處理: {total_count} 個圖片")
    print(f"成功下載: {success_count} 個")
    print(f"下載失敗: {failed_count} 個")
    print(f"已存在跳過: {skipped_count} 個")
    print(f"圖片儲存位置: {PHOTOS_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("藥物圖片下載工具")
    print("=" * 60)

    try:
        process_csv_and_download()
    except KeyboardInterrupt:
        print("\n\n使用者中斷下載")
    except Exception as e:
        print(f"\n錯誤: {str(e)}")
        import traceback

        traceback.print_exc()
