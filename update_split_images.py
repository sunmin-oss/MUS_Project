"""
============================================================================
藥物辨識系統 - 圖片分割資料庫更新工具 (update_split_images.py)
============================================================================

【檔案功能】
當手動將藥物圖片分割成多張後，此工具會自動更新資料庫記錄，
確保系統能正確辨識分割後的圖片。

【使用情境】
原本的藥物圖片可能包含兩顆藥丸並排，為了提高辨識準確度，
可以將一張圖片分割成兩張單獨的藥丸圖片。

【處理流程】
1. 手動分割圖片
   原始: 內衛成製字第XXXXX號.jpg
   分割: 內衛成製字第XXXXX號_1.jpg (左側藥丸)
        內衛成製字第XXXXX號_2.jpg (右側藥丸)

2. 執行此工具
   python update_split_images.py

3. 自動處理
   - 掃描 medicine_photos 資料夾中所有 _1.jpg 和 _2.jpg 檔案
   - 更新原始資料庫記錄的檔案名稱為 _1.jpg
   - 新增 _2.jpg 的資料庫記錄
   - 驗證更新結果

【主要功能】
1. 自動掃描分割圖片
   - 找出所有 _1.jpg 檔案
   - 檢查對應的 _2.jpg 是否存在

2. 資料庫自動更新
   - 更新原始記錄 → _1.jpg
   - 新增第二張圖片記錄 → _2.jpg
   - 保持 drug_id 關聯正確

3. 完整性驗證
   - 檢查更新數量
   - 驗證檔案存在性
   - 顯示處理結果統計

【輸出範例】
    處理: 內衛成製字第000075號
      ✅ 已更新: 內衛成製字第000075號.jpg
                → 內衛成製字第000075號_1.jpg
                + 內衛成製字第000075號_2.jpg

    ✅ 更新: 15 個藥物
    ➕ 新增: 15 筆記錄
    ⏭️  跳過: 3 個檔案

【注意事項】
- 執行前請先手動分割圖片並放入 medicine_photos 資料夾
- 檔案命名必須遵循 _1.jpg 和 _2.jpg 格式
- 建議先備份資料庫再執行
- 此工具會修改資料庫，請謹慎使用

【分割圖片的好處】
- 提高辨識準確度 (預期提升 20-30%)
- 減少背景噪音干擾
- 增強顏色與形狀特徵辨識
- 改善特徵提取精確度

【作者】MUS_Project 團隊
【日期】2024-2025
============================================================================
"""

import sqlite3
from pathlib import Path
import os


def update_database_for_split_images():
    """
    掃描 medicine_photos 資料夾,找出所有 _1.jpg 和 _2.jpg 的圖片
    自動更新資料庫記錄
    """
    db_path = "drug_recognition.db"
    photo_dir = Path("medicine_photos")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 找出所有 _1.jpg 檔案
    split_files = {}
    for file in photo_dir.glob("*_1.jpg"):
        base_name = file.stem[:-2]  # 移除 _1
        original_name = f"{base_name}.jpg"
        split_files[base_name] = {
            "original": original_name,
            "file_1": f"{base_name}_1.jpg",
            "file_2": f"{base_name}_2.jpg",
            "has_2": (photo_dir / f"{base_name}_2.jpg").exists(),
        }

    print("=" * 70)
    print("掃描到的分割圖片:")
    print("=" * 70)

    updated_count = 0
    added_count = 0
    skipped_count = 0

    for base_name, files in split_files.items():
        print(f"\n處理: {base_name}")

        if not files["has_2"]:
            print(f"  ⚠️ 跳過: 找不到 {files['file_2']}")
            skipped_count += 1
            continue

        # 檢查原始檔案是否在資料庫中
        cursor.execute(
            """
            SELECT drug_id, id 
            FROM drug_images 
            WHERE image_filename = ?
        """,
            (files["original"],),
        )

        original_record = cursor.fetchone()

        if original_record:
            drug_id, original_id = original_record

            # 檢查是否已經有 _1 和 _2 的記錄
            cursor.execute(
                """
                SELECT COUNT(*) 
                FROM drug_images 
                WHERE drug_id = ? AND (image_filename = ? OR image_filename = ?)
            """,
                (drug_id, files["file_1"], files["file_2"]),
            )

            existing_count = cursor.fetchone()[0]

            if existing_count == 2:
                print(f"  ✓ 已存在兩筆記錄,跳過")
                skipped_count += 1
                continue

            # 更新原始記錄為 _1
            cursor.execute(
                """
                UPDATE drug_images 
                SET image_filename = ?,
                    image_path = ?
                WHERE id = ?
            """,
                (files["file_1"], f"medicine_photos\\{files['file_1']}", original_id),
            )

            # 新增 _2 記錄
            cursor.execute(
                """
                INSERT INTO drug_images (drug_id, image_filename, image_path, image_order)
                VALUES (?, ?, ?, ?)
            """,
                (drug_id, files["file_2"], f"medicine_photos\\{files['file_2']}", 2),
            )

            print(
                f"  ✅ 已更新: {files['original']} → {files['file_1']} + {files['file_2']}"
            )
            updated_count += 1
        else:
            # 原始記錄不存在,檢查是否已經有 _1 記錄
            cursor.execute(
                """
                SELECT drug_id 
                FROM drug_images 
                WHERE image_filename = ?
            """,
                (files["file_1"],),
            )

            record_1 = cursor.fetchone()

            if record_1:
                drug_id = record_1[0]

                # 檢查是否已有 _2 記錄
                cursor.execute(
                    """
                    SELECT COUNT(*) 
                    FROM drug_images 
                    WHERE drug_id = ? AND image_filename = ?
                """,
                    (drug_id, files["file_2"]),
                )

                if cursor.fetchone()[0] == 0:
                    # 新增 _2 記錄
                    cursor.execute(
                        """
                        INSERT INTO drug_images (drug_id, image_filename, image_path, image_order)
                        VALUES (?, ?, ?, ?)
                    """,
                        (
                            drug_id,
                            files["file_2"],
                            f"medicine_photos\\{files['file_2']}",
                            2,
                        ),
                    )

                    print(f"  ✅ 已新增第二張: {files['file_2']}")
                    added_count += 1
                else:
                    print(f"  ✓ 兩筆記錄都已存在,跳過")
                    skipped_count += 1
            else:
                print(f"  ⚠️ 找不到對應的藥物記錄")
                skipped_count += 1

    conn.commit()
    conn.close()

    print("\n" + "=" * 70)
    print("處理完成!")
    print("=" * 70)
    print(f"✅ 更新: {updated_count} 個藥物")
    print(f"➕ 新增: {added_count} 筆記錄")
    print(f"⏭️  跳過: {skipped_count} 個檔案")
    print("=" * 70)


def verify_database():
    """驗證資料庫狀態"""
    conn = sqlite3.connect("drug_recognition.db")
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("資料庫驗證:")
    print("=" * 70)

    # 檢查有多張圖片的藥物
    cursor.execute(
        """
        SELECT drug_id, COUNT(*) as cnt 
        FROM drug_images 
        GROUP BY drug_id 
        HAVING cnt > 1
    """
    )

    multi_image_drugs = cursor.fetchall()
    print(f"有多張圖片的藥物: {len(multi_image_drugs)} 個")

    # 檢查 _1, _2 圖片
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM drug_images 
        WHERE image_filename LIKE '%_1.jpg' OR image_filename LIKE '%_2.jpg'
    """
    )

    split_images = cursor.fetchone()[0]
    print(f"分割圖片總數: {split_images} 張")

    # 檢查檔案是否存在
    cursor.execute("SELECT image_filename FROM drug_images")
    missing_files = []
    photo_dir = Path("medicine_photos")

    for row in cursor.fetchall():
        filename = row[0]
        if not (photo_dir / filename).exists():
            missing_files.append(filename)

    if missing_files:
        print(f"\n⚠️ 找不到的檔案 ({len(missing_files)} 個):")
        for f in missing_files[:10]:  # 只顯示前10個
            print(f"  - {f}")
        if len(missing_files) > 10:
            print(f"  ... 還有 {len(missing_files) - 10} 個")
    else:
        print("\n✅ 所有資料庫記錄的檔案都存在")

    conn.close()


if __name__ == "__main__":
    print("🔧 圖片分割後資料庫更新工具")
    print()
    print("此工具會:")
    print("1. 掃描 medicine_photos 資料夾中所有 _1.jpg 和 _2.jpg 檔案")
    print("2. 自動更新資料庫,將原始記錄改為 _1,並新增 _2 記錄")
    print("3. 驗證資料庫完整性")
    print()

    response = input("是否繼續? (y/n): ").strip().lower()

    if response == "y":
        update_database_for_split_images()
        verify_database()
    else:
        print("已取消")
