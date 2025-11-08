"""
為藥物資料庫新增臨床欄位的遷移腳本
執行方式: python add_clinical_fields.py
"""

import sqlite3
import os
from pathlib import Path

# 資料庫路徑
DB_PATH = Path(__file__).parent.parent / "drug_recognition.db"


def check_column_exists(cursor, table_name, column_name):
    """檢查欄位是否已存在"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def add_clinical_fields():
    """新增臨床欄位到 drugs 資料表"""

    if not DB_PATH.exists():
        print(f"❌ 找不到資料庫檔案: {DB_PATH}")
        return False

    print(f"📂 資料庫路徑: {DB_PATH}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 定義要新增的欄位
        new_fields = [
            ("indications", "TEXT", "適應症"),
            ("dosage", "TEXT", "用法用量"),
            ("side_effects", "TEXT", "副作用"),
            ("contraindications", "TEXT", "禁忌症"),
            ("precautions", "TEXT", "注意事項"),
            ("ingredient", "TEXT", "主要成分"),
            ("category", "TEXT", "藥品分類"),
            ("manufacturer", "TEXT", "製造商"),
            ("storage_conditions", "TEXT", "儲存條件"),
            ("expiry_info", "TEXT", "有效期限"),
        ]

        added_count = 0
        skipped_count = 0

        for field_name, field_type, field_desc in new_fields:
            if check_column_exists(cursor, "drugs", field_name):
                print(f"⏭️  欄位已存在，跳過: {field_name} ({field_desc})")
                skipped_count += 1
            else:
                sql = f"ALTER TABLE drugs ADD COLUMN {field_name} {field_type}"
                cursor.execute(sql)
                print(f"✅ 成功新增欄位: {field_name} ({field_desc})")
                added_count += 1

        conn.commit()

        # 顯示更新後的資料表結構
        print("\n" + "=" * 60)
        print("📋 更新後的 drugs 資料表結構:")
        print("=" * 60)
        cursor.execute("PRAGMA table_info(drugs)")
        for row in cursor.fetchall():
            col_id, col_name, col_type, not_null, default, pk = row
            nullable = "NOT NULL" if not_null else "NULL"
            pk_mark = " (主鍵)" if pk else ""
            print(f"  {col_name:<25} {col_type:<10} {nullable}{pk_mark}")

        print("\n" + "=" * 60)
        print(f"✅ 遷移完成!")
        print(f"  - 新增欄位: {added_count} 個")
        print(f"  - 已存在欄位: {skipped_count} 個")
        print("=" * 60)

        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ 資料庫錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False


def main():
    print("=" * 60)
    print("  藥物資料庫欄位擴充工具")
    print("  新增臨床資訊欄位 (適應症、用法用量、副作用等)")
    print("=" * 60)
    print()

    success = add_clinical_fields()

    if success:
        print("\n💡 提示:")
        print("  1. 資料庫結構已更新，新增欄位預設為 NULL")
        print("  2. 請同步更新 C# 管理系統的 UI 和資料存取層")
        print("  3. 建議重新編譯並測試管理系統")
    else:
        print("\n❌ 遷移失敗，請檢查錯誤訊息")


if __name__ == "__main__":
    main()
