"""
測試藥物圖片辨識功能
"""

from image_recognition import DrugImageRecognizer
from pathlib import Path


def test_single_drug_recognition():
    """測試單藥物辨識"""
    print("=" * 50)
    print("測試單藥物辨識")
    print("=" * 50)

    recognizer = DrugImageRecognizer()

    # 尋找 medicine_photos 中的第一張圖片進行測試
    photo_dir = Path("medicine_photos")

    if not photo_dir.exists():
        print("❌ medicine_photos 資料夾不存在")
        print("請先執行 python download_medicine_photos.py 下載圖片")
        return

    test_images = list(photo_dir.glob("*.jpg"))[:3]  # 取前 3 張測試

    if not test_images:
        print("❌ medicine_photos 資料夾中沒有圖片")
        return

    for test_image in test_images:
        print(f"\n📸 測試圖片: {test_image.name}")
        print("-" * 50)

        results = recognizer.recognize_drug(str(test_image), top_k=3)

        if not results:
            print("⚠️  未找到匹配結果")
            continue

        print(f"✅ 找到 {len(results)} 個匹配結果：\n")

        for i, result in enumerate(results, 1):
            print(f"第 {i} 名：")
            print(f"  藥物名稱：{result['chinese_name']}")
            if result["english_name"]:
                print(f"  英文名稱：{result['english_name']}")
            print(f"  許可證字號：{result['license_number']}")
            print(f"  形狀：{result['shape'] or '未知'}")
            print(f"  顏色：{result['color'] or '未知'}")
            print(f"  相似度：{result['similarity_percent']}")
            print()


def test_database_images_count():
    """檢查資料庫中有圖片的藥物數量"""
    print("=" * 50)
    print("檢查資料庫圖片狀態")
    print("=" * 50)

    import sqlite3

    conn = sqlite3.connect("drug_recognition.db")
    cursor = conn.cursor()

    # 檢查藥物總數
    cursor.execute("SELECT COUNT(*) FROM drugs")
    total_drugs = cursor.fetchone()[0]

    # 檢查有圖片的藥物數
    cursor.execute(
        """
        SELECT COUNT(DISTINCT drug_id) 
        FROM drug_images
    """
    )
    drugs_with_images = cursor.fetchone()[0]

    # 檢查圖片總數
    cursor.execute("SELECT COUNT(*) FROM drug_images")
    total_images = cursor.fetchone()[0]

    # 檢查實際存在的圖片
    photo_dir = Path("medicine_photos")
    if photo_dir.exists():
        actual_images = len(list(photo_dir.glob("*.jpg"))) + len(
            list(photo_dir.glob("*.png"))
        )
    else:
        actual_images = 0

    conn.close()

    print(f"📊 資料庫統計：")
    print(f"  總藥物數：{total_drugs}")
    print(f"  有圖片記錄的藥物：{drugs_with_images}")
    print(f"  圖片記錄總數：{total_images}")
    print(f"  實際圖片檔案：{actual_images}")
    print()

    if actual_images == 0:
        print("⚠️  沒有實際圖片檔案")
        print("建議執行：python download_medicine_photos.py")
    elif actual_images < total_images:
        print(f"⚠️  缺少 {total_images - actual_images} 張圖片")
    else:
        print("✅ 圖片完整")


def print_usage():
    """列印使用說明"""
    print("=" * 50)
    print("藥物圖片辨識功能使用說明")
    print("=" * 50)
    print()
    print("📝 API 端點：POST /api/recognize")
    print()
    print("參數：")
    print("  - image: 圖片檔案（必需）")
    print("  - top_k: 返回前 K 個結果（預設 5）")
    print("  - is_prescription: 是否為藥單模式（true/false，預設 false）")
    print()
    print("📌 使用方式：")
    print("  1. 在前端上傳藥物圖片")
    print("  2. 點擊「辨識藥物」按鈕")
    print("  3. 系統會顯示最相似的藥物列表")
    print()
    print("🔧 本地測試：")
    print("  python test_recognition.py")
    print()


if __name__ == "__main__":
    print_usage()
    print()
    test_database_images_count()
    print()

    # 詢問是否進行辨識測試
    answer = input("是否進行辨識測試？(y/n): ").strip().lower()
    if answer == "y":
        test_single_drug_recognition()
