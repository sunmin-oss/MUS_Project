"""
將 medicine_photos/ 中已下載的圖片與資料庫(drug_images)同步
使用情境：
- 先建立過資料庫，後來才下載圖片，導致搜尋結果沒有圖片
- 不想刪除重建整個資料庫，只想補上圖片對應

使用方法（PowerShell）：
  cd "d:\大學\專題\MUS_Project"
  python sync_images.py

選項：
  --force  重新掃描並覆蓋該藥物現有的圖片記錄
"""

import os
import sqlite3
from pathlib import Path
import argparse

DB_FILE = "drug_recognition.db"
IMAGE_FOLDER = Path("medicine_photos")


def find_image_files(license_number: str):
    """依許可證字號尋找所有對應圖片檔名"""
    if not IMAGE_FOLDER.exists():
        return []

    def exists(name):
        return any(
            (IMAGE_FOLDER / f"{name}{ext}").exists()
            for ext in [".jpg", ".jpeg", ".png", ".gif"]
        )

    files = []

    # 主圖
    for ext in [".jpg", ".jpeg", ".png", ".gif"]:
        main_file = f"{license_number}{ext}"
        if (IMAGE_FOLDER / main_file).exists():
            files.append(main_file)
            break

    # 編號圖
    idx = 1
    while True:
        found = False
        for ext in [".jpg", ".jpeg", ".png", ".gif"]:
            numbered = f"{license_number}_{idx}{ext}"
            if (IMAGE_FOLDER / numbered).exists():
                files.append(numbered)
                found = True
                break
        if not found:
            break
        idx += 1

    return files


def sync_images(force: bool = False):
    if not Path(DB_FILE).exists():
        print(f"✗ 找不到資料庫 {DB_FILE}，請先執行 create_database.py")
        return

    if not IMAGE_FOLDER.exists():
        print(
            f"✗ 找不到圖片資料夾 {IMAGE_FOLDER}，請先執行 download_medicine_photos.py"
        )
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 取得所有藥物（id, license_number, chinese_name）
    c.execute("SELECT id, license_number, chinese_name FROM drugs")
    drugs = c.fetchall()

    updated = 0
    inserted = 0
    skipped = 0

    for drug_id, license_number, cname in drugs:
        # 取得現有圖片數
        c.execute("SELECT COUNT(*) FROM drug_images WHERE drug_id = ?", (drug_id,))
        count = c.fetchone()[0]

        # 若已有圖片且非強制模式則跳過
        if count > 0 and not force:
            skipped += 1
            continue

        files = find_image_files(license_number)

        if not files:
            continue

        if force and count > 0:
            c.execute("DELETE FROM drug_images WHERE drug_id = ?", (drug_id,))
            updated += 1

        # 寫入圖片記錄
        for idx, filename in enumerate(files, start=1):
            image_path = str(IMAGE_FOLDER / filename)
            c.execute(
                """
                INSERT INTO drug_images (drug_id, image_filename, image_path, image_order)
                VALUES (?, ?, ?, ?)
                """,
                (drug_id, filename, image_path, idx),
            )
            inserted += 1

    conn.commit()
    conn.close()

    print("\n=== 同步結果 ===")
    print(f"新增圖片記錄: {inserted}")
    print(f"覆寫圖片的藥物數: {updated}")
    print(f"跳過（已有圖片）: {skipped}")
    print("完成！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="覆寫已存在的圖片記錄")
    args = parser.parse_args()
    sync_images(force=args.force)
