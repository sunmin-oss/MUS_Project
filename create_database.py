"""
藥物資料庫建立與資料導入腳本 (SQLite 版本)
"""

import sqlite3
import csv
import os
from pathlib import Path

# SQLite 資料庫檔案
DB_FILE = "drug_recognition.db"

# CSV 檔案路徑
CSV_FILE = "medicine_data.csv"
IMAGE_FOLDER = "medicine_photos"


def create_database_schema(conn):
    """建立資料庫結構"""
    cursor = conn.cursor()

    # 建立藥物基本資料表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_number TEXT UNIQUE NOT NULL,
            chinese_name TEXT NOT NULL,
            english_name TEXT,
            shape TEXT,
            special_dosage_form TEXT,
            color TEXT,
            special_odor TEXT,
            mark TEXT,
            size TEXT,
            label_front TEXT,
            label_back TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # 建立藥物圖片表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS drug_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_id INTEGER NOT NULL,
            image_filename TEXT NOT NULL,
            image_path TEXT NOT NULL,
            image_order INTEGER DEFAULT 1,
            feature_vector TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (drug_id) REFERENCES drugs(id) ON DELETE CASCADE
        )
    """
    )

    # 建立索引
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_drugs_license ON drugs(license_number)",
        "CREATE INDEX IF NOT EXISTS idx_drugs_chinese_name ON drugs(chinese_name)",
        "CREATE INDEX IF NOT EXISTS idx_drugs_english_name ON drugs(english_name)",
        "CREATE INDEX IF NOT EXISTS idx_drugs_color ON drugs(color)",
        "CREATE INDEX IF NOT EXISTS idx_drugs_shape ON drugs(shape)",
        "CREATE INDEX IF NOT EXISTS idx_drug_images_drug_id ON drug_images(drug_id)",
        "CREATE INDEX IF NOT EXISTS idx_drug_images_filename ON drug_images(image_filename)",
    ]

    for index_sql in indexes:
        cursor.execute(index_sql)

    conn.commit()
    print("✓ 資料庫結構建立完成")


def import_csv_data(conn):
    """從 CSV 匯入資料"""
    cursor = conn.cursor()

    # 讀取 CSV 檔案
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        csv_reader = csv.DictReader(f)

        imported_count = 0
        skipped_count = 0
        error_count = 0

        for row in csv_reader:
            try:
                license_number = row["許可證字號"].strip()

                if not license_number:
                    continue

                # 檢查是否已存在
                cursor.execute(
                    "SELECT id FROM drugs WHERE license_number = ?", (license_number,)
                )
                existing = cursor.fetchone()

                if existing:
                    print(f"⚠ 跳過已存在的藥物: {license_number}")
                    skipped_count += 1
                    continue

                # 插入藥物基本資料
                cursor.execute(
                    """
                    INSERT INTO drugs (
                        license_number, chinese_name, english_name, 
                        shape, special_dosage_form, color, special_odor,
                        mark, size, label_front, label_back
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        license_number,
                        row["中文品名"].strip(),
                        row["英文品名"].strip() if row["英文品名"].strip() else None,
                        row["形狀"].strip() if row["形狀"].strip() else None,
                        row["特殊劑型"].strip() if row["特殊劑型"].strip() else None,
                        row["顏色"].strip() if row["顏色"].strip() else None,
                        row["特殊氣味"].strip() if row["特殊氣味"].strip() else None,
                        row["刻痕"].strip() if row["刻痕"].strip() else None,
                        row["外觀尺寸"].strip() if row["外觀尺寸"].strip() else None,
                        row["標註一"].strip() if row["標註一"].strip() else None,
                        row["標註二"].strip() if row["標註二"].strip() else None,
                    ),
                )

                drug_id = cursor.lastrowid

                # 檢查並插入圖片資料
                image_files = find_image_files(license_number)
                for idx, image_file in enumerate(image_files, start=1):
                    image_path = os.path.join(IMAGE_FOLDER, image_file)
                    cursor.execute(
                        """
                        INSERT INTO drug_images (drug_id, image_filename, image_path, image_order)
                        VALUES (?, ?, ?, ?)
                    """,
                        (drug_id, image_file, image_path, idx),
                    )

                imported_count += 1
                if imported_count % 100 == 0:
                    print(f"已匯入 {imported_count} 筆資料...")
                    conn.commit()  # 每 100 筆提交一次

            except Exception as e:
                print(f"✗ 匯入失敗 {row.get('許可證字號', 'Unknown')}: {e}")
                error_count += 1
                continue

        conn.commit()
        print(f"\n✓ 資料匯入完成!")
        print(f"  - 成功匯入: {imported_count} 筆")
        print(f"  - 跳過: {skipped_count} 筆")
        print(f"  - 錯誤: {error_count} 筆")


def find_image_files(license_number):
    """尋找特定許可證號碼的所有圖片檔案"""
    image_folder = Path(IMAGE_FOLDER)
    if not image_folder.exists():
        return []

    # 尋找主要圖片和編號圖片
    image_files = []

    # 尋找基本檔名的圖片（例如：內衛藥製字第000102號.jpg）
    for ext in [".jpg", ".jpeg", ".png", ".gif"]:
        main_file = f"{license_number}{ext}"
        if (image_folder / main_file).exists():
            image_files.append(main_file)
            break

    # 尋找編號圖片（例如：內衛藥製字第000102號_1.jpg, 內衛藥製字第000102號_2.jpg）
    idx = 1
    while True:
        found = False
        for ext in [".jpg", ".jpeg", ".png", ".gif"]:
            numbered_file = f"{license_number}_{idx}{ext}"
            if (image_folder / numbered_file).exists():
                image_files.append(numbered_file)
                found = True
                break
        if not found:
            break
        idx += 1

    return image_files


def verify_data(conn):
    """驗證資料匯入結果"""
    cursor = conn.cursor()

    # 統計藥物數量
    cursor.execute("SELECT COUNT(*) FROM drugs")
    drug_count = cursor.fetchone()[0]

    # 統計圖片數量
    cursor.execute("SELECT COUNT(*) FROM drug_images")
    image_count = cursor.fetchone()[0]

    # 統計有圖片的藥物數量
    cursor.execute(
        """
        SELECT COUNT(DISTINCT drug_id) FROM drug_images
    """
    )
    drugs_with_images = cursor.fetchone()[0]

    print("\n=== 資料庫統計 ===")
    print(f"藥物總數: {drug_count}")
    print(f"圖片總數: {image_count}")
    print(f"有圖片的藥物: {drugs_with_images}")
    print(f"無圖片的藥物: {drug_count - drugs_with_images}")

    # 顯示一些範例資料
    cursor.execute(
        """
        SELECT d.license_number, d.chinese_name, COUNT(di.id) as image_count
        FROM drugs d
        LEFT JOIN drug_images di ON d.id = di.drug_id
        GROUP BY d.id, d.license_number, d.chinese_name
        ORDER BY image_count DESC
        LIMIT 5
    """
    )

    print("\n=== 圖片最多的藥物（前5名）===")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}: {row[2]} 張圖片")


def main():
    """主程式"""
    print("=== 藥物資料庫建立程式 ===\n")

    try:
        # 連接資料庫
        print("連接資料庫...")
        conn = sqlite3.connect(DB_FILE)
        print("✓ 資料庫連接成功\n")

        # 建立資料庫結構
        print("建立資料庫結構...")
        create_database_schema(conn)
        print()

        # 匯入資料
        print("開始匯入資料...")
        import_csv_data(conn)
        print()

        # 驗證資料
        print("驗證資料...")
        verify_data(conn)

        conn.close()
        print("\n✓ 所有操作完成!")

    except sqlite3.Error as e:
        print(f"✗ 資料庫錯誤: {e}")
    except FileNotFoundError as e:
        print(f"✗ 檔案不存在: {e}")
    except Exception as e:
        print(f"✗ 發生錯誤: {e}")


if __name__ == "__main__":
    main()
