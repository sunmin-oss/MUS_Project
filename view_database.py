"""
簡單的資料庫查看工具
"""

import sqlite3
import sys

DB_FILE = "drug_recognition.db"


def show_tables():
    """顯示所有資料表"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\n=== 資料表列表 ===")
    for table in tables:
        print(f"  - {table[0]}")
    conn.close()


def show_schema(table_name):
    """顯示資料表結構"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\n=== {table_name} 資料表結構 ===")
    print(f"{'欄位名稱':<20} {'資料型別':<15} {'是否必填':<10} {'主鍵':<5}")
    print("-" * 60)
    for col in columns:
        cid, name, dtype, notnull, dflt_value, pk = col
        print(
            f"{name:<20} {dtype:<15} {'NOT NULL' if notnull else '':<10} {'是' if pk else '':<5}"
        )
    conn.close()


def show_count(table_name):
    """顯示資料表筆數"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\n{table_name} 資料表共有 {count} 筆資料")
    conn.close()


def show_sample_data(table_name, limit=5):
    """顯示範例資料"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()

    print(f"\n=== {table_name} 範例資料（前 {limit} 筆）===")
    for i, row in enumerate(rows, 1):
        print(f"\n第 {i} 筆：")
        for key in row.keys():
            value = row[key]
            if value and len(str(value)) > 50:
                value = str(value)[:50] + "..."
            print(f"  {key}: {value}")

    conn.close()


def search_by_name(keyword):
    """根據名稱搜索"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT d.license_number, d.chinese_name, d.english_name, 
               d.shape, d.color, COUNT(di.id) as image_count
        FROM drugs d
        LEFT JOIN drug_images di ON d.id = di.drug_id
        WHERE d.chinese_name LIKE ? OR d.english_name LIKE ?
        GROUP BY d.id
        LIMIT 10
    """,
        (f"%{keyword}%", f"%{keyword}%"),
    )

    results = cursor.fetchall()
    print(f"\n=== 搜索結果：{keyword} ===")
    if results:
        for row in results:
            print(f"\n許可證: {row['license_number']}")
            print(f"中文名: {row['chinese_name']}")
            print(f"英文名: {row['english_name']}")
            print(f"形狀: {row['shape']}, 顏色: {row['color']}")
            print(f"圖片數: {row['image_count']}")
    else:
        print("找不到符合的藥物")

    conn.close()


def show_statistics():
    """顯示統計資訊"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("\n=== 資料庫統計 ===")

    # 藥物總數
    cursor.execute("SELECT COUNT(*) FROM drugs")
    print(f"藥物總數: {cursor.fetchone()[0]}")

    # 圖片總數
    cursor.execute("SELECT COUNT(*) FROM drug_images")
    print(f"圖片總數: {cursor.fetchone()[0]}")

    # 有圖片的藥物
    cursor.execute("SELECT COUNT(DISTINCT drug_id) FROM drug_images")
    print(f"有圖片的藥物: {cursor.fetchone()[0]}")

    # 顏色分布（前10名）
    cursor.execute(
        """
        SELECT color, COUNT(*) as count
        FROM drugs
        WHERE color IS NOT NULL AND color != ''
        GROUP BY color
        ORDER BY count DESC
        LIMIT 10
    """
    )
    print("\n顏色分布（前10名）:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} 個")

    # 形狀分布（前10名）
    cursor.execute(
        """
        SELECT shape, COUNT(*) as count
        FROM drugs
        WHERE shape IS NOT NULL AND shape != ''
        GROUP BY shape
        ORDER BY count DESC
        LIMIT 10
    """
    )
    print("\n形狀分布（前10名）:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} 個")

    conn.close()


def show_menu():
    """顯示選單"""
    print("\n" + "=" * 50)
    print("藥物資料庫查看工具")
    print("=" * 50)
    print("1. 顯示所有資料表")
    print("2. 顯示 drugs 資料表結構")
    print("3. 顯示 drug_images 資料表結構")
    print("4. 顯示資料筆數")
    print("5. 顯示 drugs 範例資料")
    print("6. 顯示 drug_images 範例資料")
    print("7. 搜索藥物（依名稱）")
    print("8. 顯示統計資訊")
    print("9. 執行自訂 SQL 查詢")
    print("0. 離開")
    print("=" * 50)


def execute_custom_query():
    """執行自訂 SQL 查詢"""
    print("\n請輸入 SQL 查詢語句：")
    query = input("> ")

    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)

        if query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            print(f"\n查詢結果（共 {len(results)} 筆）：")
            for i, row in enumerate(results[:20], 1):  # 最多顯示20筆
                print(f"\n第 {i} 筆：")
                for key in row.keys():
                    print(f"  {key}: {row[key]}")
            if len(results) > 20:
                print(f"\n... 還有 {len(results) - 20} 筆資料未顯示")
        else:
            conn.commit()
            print(f"查詢執行成功，影響 {cursor.rowcount} 筆資料")

        conn.close()
    except Exception as e:
        print(f"錯誤: {e}")


def main():
    """主程式"""
    while True:
        show_menu()
        choice = input("\n請選擇功能 (0-9): ").strip()

        if choice == "1":
            show_tables()
        elif choice == "2":
            show_schema("drugs")
        elif choice == "3":
            show_schema("drug_images")
        elif choice == "4":
            show_count("drugs")
            show_count("drug_images")
        elif choice == "5":
            limit = input("要顯示幾筆資料？(預設5): ").strip()
            limit = int(limit) if limit else 5
            show_sample_data("drugs", limit)
        elif choice == "6":
            limit = input("要顯示幾筆資料？(預設5): ").strip()
            limit = int(limit) if limit else 5
            show_sample_data("drug_images", limit)
        elif choice == "7":
            keyword = input("請輸入搜索關鍵字: ").strip()
            if keyword:
                search_by_name(keyword)
        elif choice == "8":
            show_statistics()
        elif choice == "9":
            execute_custom_query()
        elif choice == "0":
            print("\n再見！")
            break
        else:
            print("\n無效的選擇，請重新輸入")

        input("\n按 Enter 繼續...")


if __name__ == "__main__":
    main()
