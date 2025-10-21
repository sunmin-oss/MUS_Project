"""
藥物圖片辨識模組
支援多種辨識方法：特徵比對、OCR 文字辨識
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sqlite3
from database_query import DrugDatabase


class DrugImageRecognizer:
    """藥物圖片辨識器（特徵比對方法）"""

    def __init__(
        self, db_path: str = "drug_recognition.db", photo_dir: str = "medicine_photos"
    ):
        self.db_path = db_path
        self.photo_dir = Path(photo_dir)

    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        預處理圖片：調整大小、去噪

        Args:
            image_path: 圖片路徑

        Returns:
            處理後的圖片陣列，失敗返回 None
        """
        try:
            # 使用 cv2.imdecode 處理中文路徑
            import numpy as np

            # 讀取圖片（支援中文路徑）
            with open(image_path, "rb") as f:
                image_data = f.read()
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                return None

            # 調整大小（標準化）
            img = cv2.resize(img, (300, 300))

            # 降噪
            img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

            return img
        except Exception as e:
            print(f"圖片預處理失敗: {e}")
            return None

    def extract_color_histogram(self, image: np.ndarray) -> np.ndarray:
        """
        提取顏色直方圖特徵

        Args:
            image: 圖片陣列

        Returns:
            顏色直方圖特徵向量
        """
        # 轉換到 HSV 色彩空間
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 計算直方圖
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])

        # 正規化
        hist = cv2.normalize(hist, hist).flatten()

        return hist

    def extract_shape_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        提取形狀特徵

        Args:
            image: 圖片陣列

        Returns:
            形狀特徵字典
        """
        # 轉為灰階
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 二值化
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 尋找輪廓
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return {"area": 0, "perimeter": 0, "circularity": 0}

        # 取最大輪廓
        main_contour = max(contours, key=cv2.contourArea)

        # 計算特徵
        area = cv2.contourArea(main_contour)
        perimeter = cv2.arcLength(main_contour, True)
        circularity = 4 * np.pi * area / (perimeter**2) if perimeter > 0 else 0

        return {"area": area, "perimeter": perimeter, "circularity": circularity}

    def calculate_similarity(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """
        計算兩個直方圖的相似度（使用相關性）

        Args:
            hist1: 第一個直方圖
            hist2: 第二個直方圖

        Returns:
            相似度分數 (0-1)
        """
        # 使用相關性方法
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        # 轉換到 0-1 範圍
        return max(0, similarity)

    def recognize_drug(self, uploaded_image_path: str, top_k: int = 5) -> List[Dict]:
        """
        辨識上傳的藥物圖片

        Args:
            uploaded_image_path: 上傳圖片的路徑
            top_k: 返回前 K 個最相似的結果

        Returns:
            辨識結果列表，每項包含藥物資訊和相似度
        """
        # 預處理上傳的圖片
        uploaded_img = self.preprocess_image(uploaded_image_path)
        if uploaded_img is None:
            return []

        # 提取上傳圖片的特徵
        uploaded_hist = self.extract_color_histogram(uploaded_img)
        uploaded_shape = self.extract_shape_features(uploaded_img)

        # 獲取所有有圖片的藥物
        results = []

        with DrugDatabase(self.db_path) as db:
            # 獲取所有藥物及其圖片
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DISTINCT d.id, d.chinese_name, d.english_name, d.license_number,
                       d.shape, d.color, d.special_dosage_form, i.image_filename
                FROM drugs d
                INNER JOIN drug_images i ON d.id = i.drug_id
            """
            )

            drugs_with_images = cursor.fetchall()
            conn.close()

            # 對每個藥物圖片進行比對
            for drug_data in drugs_with_images:
                (
                    drug_id,
                    chinese_name,
                    english_name,
                    license_number,
                    shape,
                    color,
                    dosage_form,
                    image_filename,
                ) = drug_data

                # 構建圖片路徑
                image_path = self.photo_dir / image_filename

                if not image_path.exists():
                    continue

                # 預處理資料庫圖片
                db_img = self.preprocess_image(str(image_path))
                if db_img is None:
                    continue

                # 提取資料庫圖片特徵
                db_hist = self.extract_color_histogram(db_img)
                db_shape = self.extract_shape_features(db_img)

                # 計算相似度
                color_similarity = self.calculate_similarity(uploaded_hist, db_hist)

                # 形狀相似度（簡單比較圓度）
                shape_similarity = 1 - abs(
                    uploaded_shape["circularity"] - db_shape["circularity"]
                )

                # 綜合相似度（顏色權重 0.7，形狀權重 0.3）
                overall_similarity = 0.7 * color_similarity + 0.3 * shape_similarity

                results.append(
                    {
                        "drug_id": drug_id,
                        "chinese_name": chinese_name,
                        "english_name": english_name,
                        "license_number": license_number,
                        "shape": shape,
                        "color": color,
                        "special_dosage_form": dosage_form,
                        "image_filename": image_filename,
                        "similarity": float(overall_similarity),
                        "similarity_percent": f"{overall_similarity * 100:.1f}%",
                    }
                )

        # 按相似度排序並返回前 K 個
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:top_k]

    def recognize_prescription(self, uploaded_image_path: str) -> Dict:
        """
        辨識藥單（包含多個藥物的圖片）

        Args:
            uploaded_image_path: 上傳的藥單圖片路徑

        Returns:
            辨識結果，包含檢測到的多個藥物
        """
        # 讀取圖片（支援中文路徑）
        try:
            with open(uploaded_image_path, "rb") as f:
                image_data = f.read()
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return {"success": False, "message": f"無法讀取圖片: {e}"}

        if img is None:
            return {"success": False, "message": "無法讀取圖片"}

        # 轉為灰階
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 使用自適應閾值
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # 尋找輪廓（可能的藥物區域）
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # 過濾太小的輪廓
        min_area = 1000
        drug_regions = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

        # 對每個區域進行辨識
        detected_drugs = []

        for i, contour in enumerate(drug_regions[:10]):  # 最多處理 10 個區域
            # 獲取邊界框
            x, y, w, h = cv2.boundingRect(contour)

            # 裁剪藥物區域
            drug_roi = img[y : y + h, x : x + w]

            # 儲存臨時圖片
            temp_path = f"temp_drug_{i}.jpg"
            cv2.imwrite(temp_path, drug_roi)

            # 辨識該區域
            recognition_result = self.recognize_drug(temp_path, top_k=1)

            if recognition_result:
                detected_drugs.append(
                    {
                        "region": i + 1,
                        "position": {
                            "x": int(x),
                            "y": int(y),
                            "w": int(w),
                            "h": int(h),
                        },
                        "drug": recognition_result[0],
                    }
                )

            # 清理臨時檔案
            Path(temp_path).unlink(missing_ok=True)

        return {
            "success": True,
            "total_detected": len(detected_drugs),
            "drugs": detected_drugs,
        }


def test_recognition():
    """測試辨識功能"""
    recognizer = DrugImageRecognizer()

    # 測試單藥物辨識
    test_image = "test_drug.jpg"  # 替換為實際測試圖片路徑

    if Path(test_image).exists():
        print("開始辨識...")
        results = recognizer.recognize_drug(test_image, top_k=3)

        print(f"\n找到 {len(results)} 個匹配結果：")
        for i, result in enumerate(results, 1):
            print(f"\n第 {i} 名：")
            print(f"  藥物名稱：{result['chinese_name']} ({result['english_name']})")
            print(f"  許可證字號：{result['license_number']}")
            print(f"  相似度：{result['similarity_percent']}")
    else:
        print(f"測試圖片不存在: {test_image}")


def detect_image_type(image_path: str) -> str:
    """
    自動判斷圖片類型

    Args:
        image_path: 圖片路徑

    Returns:
        'text': 包含大量文字（藥單/藥袋）
        'object': 單一物體（藥物照片）
        'mixed': 混合或不確定
    """
    try:
        # 讀取圖片
        with open(image_path, "rb") as f:
            image_data = f.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return "mixed"

        # 轉灰階
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 邊緣檢測
        edges = cv2.Canny(gray, 50, 150)

        # 計算邊緣密度
        edge_density = np.sum(edges > 0) / edges.size

        # 輪廓檢測
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # 文字區域通常有很多小輪廓
        small_contours = sum(1 for c in contours if cv2.contourArea(c) < 500)

        # 判斷邏輯
        if edge_density > 0.15 and small_contours > 50:
            return "text"  # 可能是藥單/文件
        elif len(contours) < 10 and edge_density < 0.1:
            return "object"  # 可能是單一藥物
        else:
            return "mixed"  # 不確定
    except Exception as e:
        print(f"圖片類型判斷失敗: {e}")
        return "mixed"


if __name__ == "__main__":
    test_recognition()
