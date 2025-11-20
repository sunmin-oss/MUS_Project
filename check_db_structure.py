"""
============================================================================
藥物辨識系統 - 資料庫結構檢查工具 (check_db_structure.py)
============================================================================

【檔案功能】
這是一個診斷工具，用於檢查資料庫的結構與資料完整性。

【主要功能】
1. 顯示資料表結構
   - drug_images 資料表的欄位定義
   - 顯示欄位名稱、資料型別、是否為必填

2. 查看範例資料
   - 顯示前 5 筆資料記錄
   - 檢查資料格式是否正確

3. 檢查分割圖片
   - 列出所有 _1.jpg 和 _2.jpg 的檔案
   - 確認圖片分割後的命名是否正確

4. 統計資訊
   - 總圖片數量
   - 有圖片的藥物數量
   - 一藥多圖的情況統計

【使用時機】
- 初始化資料庫後，確認結構正確
- 新增圖片後，驗證資料完整性
- 除錯時，檢查資料異常
- 了解資料庫目前狀態

【執行方式】
    python check_db_structure.py

【輸出範例】
    drug_images 資料表結構:
    id                   INTEGER         NOT NULL
    drug_id              INTEGER         NOT NULL
    image_filename       TEXT            NOT NULL
    ...

    總圖片數: 4775
    有圖片的藥物數: 4394

【注意事項】
- 此工具為唯讀操作，不會修改資料庫
- 需要 drug_recognition.db 檔案存在於同一目錄

【作者】MUS_Project 團隊
【日期】2024-2025
============================================================================
"""

import sqlite3

conn = sqlite3.connect("drug_recognition.db")
cursor = conn.cursor()

print("=" * 60)
print("drug_images 資料表結構:")
print("=" * 60)
cursor.execute("PRAGMA table_info(drug_images)")
for row in cursor.fetchall():
    print(f"{row[1]:20} {row[2]:15} {'NOT NULL' if row[3] else ''}")

print("\n" + "=" * 60)
print("範例資料 (前5筆):")
print("=" * 60)
cursor.execute("SELECT * FROM drug_images LIMIT 5")
for row in cursor.fetchall():
    print(row)

print("\n" + "=" * 60)
print("檢查 _1, _2 檔案命名:")
print("=" * 60)
cursor.execute(
    "SELECT image_filename FROM drug_images WHERE image_filename LIKE '%_1.jpg' OR image_filename LIKE '%_2.jpg' LIMIT 10"
)
for row in cursor.fetchall():
    print(row[0])

print("\n" + "=" * 60)
print("統計:")
print("=" * 60)
cursor.execute("SELECT COUNT(*) FROM drug_images")
print(f"總圖片數: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(DISTINCT drug_id) FROM drug_images")
print(f"有圖片的藥物數: {cursor.fetchone()[0]}")

cursor.execute(
    "SELECT drug_id, COUNT(*) as cnt FROM drug_images GROUP BY drug_id HAVING cnt > 1 LIMIT 5"
)
print(f"\n有多張圖片的藥物範例:")
for row in cursor.fetchall():
    print(f"  Drug ID {row[0]}: {row[1]} 張圖片")

conn.close()
