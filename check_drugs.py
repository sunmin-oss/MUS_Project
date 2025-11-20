"""
============================================================================
藥物辨識系統 - 藥物資料檢查工具 (check_drugs.py)
============================================================================

【檔案功能】
這是一個簡易的資料庫查詢工具，用於快速查看資料庫中的藥物資料。

【主要功能】
1. 列出藥物清單
   - 顯示資料庫中前 30 個藥物名稱
   - 快速瀏覽資料庫內容

2. 關鍵字搜尋
   - 搜尋包含特定關鍵字的藥物
   - 預設關鍵字: 普拿疼、阿斯、疼、痛、感冒、胃、息、樂、咳、炎
   - 每個關鍵字最多顯示 5 筆結果

【使用時機】
- 確認資料庫中有哪些藥物
- 測試搜尋功能是否正常
- 查找特定藥物是否存在於資料庫
- 了解常用藥物的命名方式

【執行方式】
    python check_drugs.py

【輸出範例】
    === 資料庫中的前30個藥物 ===
    1. 感冒友膜衣錠
    2. 普拿疼止痛錠
    ...

    === 搜尋常見關鍵字 ===
    包含 '普拿疼' 的藥物:
      - 普拿疼止痛錠
      - 普拿疼加強錠
      ...

【注意事項】
- 此工具為唯讀操作，不會修改資料庫
- 需要 drug_recognition.db 檔案存在於同一目錄
- 可以自行修改 keywords 列表來搜尋其他關鍵字

【作者】MUS_Project 團隊
【日期】2024-2025
============================================================================
"""

import sqlite3

# 連接資料庫
conn = sqlite3.connect("drug_recognition.db")
cursor = conn.cursor()

# 查詢前30個藥物名稱
cursor.execute("SELECT chinese_name FROM drugs WHERE chinese_name IS NOT NULL LIMIT 30")
drugs = cursor.fetchall()

print("=== 資料庫中的前30個藥物 ===")
for i, drug in enumerate(drugs, 1):
    print(f"{i}. {drug[0]}")

print("\n=== 搜尋常見關鍵字 ===")
keywords = ["普拿疼", "阿斯", "疼", "痛", "感冒", "胃", "息", "樂", "咳", "炎"]

for keyword in keywords:
    cursor.execute(
        f"SELECT chinese_name FROM drugs WHERE chinese_name LIKE '%{keyword}%' LIMIT 5"
    )
    results = cursor.fetchall()
    if results:
        print(f"\n包含 '{keyword}' 的藥物:")
        for r in results:
            print(f"  - {r[0]}")

conn.close()
