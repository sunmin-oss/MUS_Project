"""
============================================================================
藥物辨識系統 - OCR 文字辨識模組 (ocr_module.py)
============================================================================

【檔案功能】
此模組使用 PaddleOCR 技術辨識藥單或藥袋上的文字，自動提取藥物名稱。

【主要功能】
1. 藥單文字辨識
   - 使用 PaddleOCR 引擎辨識圖片中的中文文字
   - 自動提取可能的藥物名稱

2. 智慧名稱匹配
   - 將辨識出的文字與資料庫中的藥物名稱比對
   - 支援部分匹配 (例如: 辨識到"普拿疼"可找到"普拿疼錠")

3. 置信度評估
   - OCR 辨識信心度評分
   - 資料庫匹配相似度評分
   - 綜合評分排序

【使用情境】
- 辨識醫師開立的處方箋
- 辨識藥局提供的藥袋
- 辨識藥盒上的藥名標示

【技術規格】
- OCR 引擎: PaddleOCR 3.3.0+
- 語言支援: 繁體中文、英文
- 辨識方向: 支援多角度文字 (angle_cls=True)

【辨識流程】
1. 上傳藥單/藥袋圖片
2. PaddleOCR 辨識所有文字區塊
3. 提取可能的藥物名稱關鍵字
4. 與資料庫比對找出匹配藥物
5. 回傳辨識結果與信心度

【使用範例】
    ocr = DrugOCRRecognizer()
    results = ocr.recognize_prescription("prescription.jpg")

    for drug in results:
        print(f"{drug['chinese_name']}: {drug['confidence']:.2f}%")

【注意事項】
- 需要安裝 PaddleOCR 和 PaddlePaddle 套件
- 首次執行會自動下載 OCR 模型 (~100MB)
- 圖片建議清晰、文字水平擺放以獲得最佳效果
- 此模組為選用功能，可獨立於影像辨識模組使用

【兼容性】
- PaddleOCR 3.3.0 已移除 use_gpu 和 show_log 參數
- 若使用舊版本可能需要調整初始化參數

【作者】MUS_Project 團隊
【日期】2024-2025
============================================================================
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
from database_query import DrugDatabase


class DrugOCRRecognizer:
    """藥單 OCR 辨識器"""

    def __init__(self, db_path: str = "drug_recognition.db"):
        self.db_path = db_path
        self.ocr = None
        self._init_ocr()

    def _init_ocr(self):
        """初始化 PaddleOCR"""
        try:
            from paddleocr import PaddleOCR

            # 初始化 OCR（使用繁體中文模型）
            # 注意：PaddleOCR 3.x 版本移除了 use_gpu 和 show_log 參數
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # 使用方向分類
                lang="ch",  # 中文模型（支援繁體）
            )
            print("✅ PaddleOCR 初始化成功")
        except ImportError:
            print("⚠️  PaddleOCR 未安裝，請執行：pip install paddleocr paddlepaddle")
            self.ocr = None
        except Exception as e:
            print(f"⚠️  PaddleOCR 初始化失敗: {e}")
            self.ocr = None

    def extract_text(self, image_path: str) -> List[Tuple[str, float]]:
        """
        從圖片中提取文字

        Args:
            image_path: 圖片路徑

        Returns:
            [(文字, 置信度)] 列表
        """
        if self.ocr is None:
            return []

        try:
            # 執行 OCR
            result = self.ocr.ocr(image_path, cls=True)

            if not result or not result[0]:
                return []

            # 提取文字和置信度
            texts = []
            for line in result[0]:
                text = line[1][0]  # 文字內容
                confidence = line[1][1]  # 置信度
                texts.append((text, confidence))

            return texts
        except Exception as e:
            print(f"OCR 提取失敗: {e}")
            return []

    def recognize_prescription(
        self, image_path: str, confidence_threshold: float = 0.7
    ) -> Dict:
        """
        辨識藥單（處方籤）

        Args:
            image_path: 藥單圖片路徑
            confidence_threshold: 置信度閾值（低於此值的文字會被過濾）

        Returns:
            辨識結果
        """
        if self.ocr is None:
            return {"success": False, "message": "OCR 模組未初始化，請安裝 paddleocr"}

        # 提取文字
        texts = self.extract_text(image_path)

        if not texts:
            return {"success": False, "message": "未能從圖片中識別文字"}

        # 過濾低置信度文字
        filtered_texts = [
            (text, conf) for text, conf in texts if conf >= confidence_threshold
        ]

        # 在資料庫中搜尋匹配的藥物
        matched_drugs = []
        all_detected_texts = []

        with DrugDatabase(self.db_path) as db:
            for text, confidence in filtered_texts:
                all_detected_texts.append(
                    {"text": text, "confidence": f"{confidence * 100:.1f}%"}
                )

                # 搜尋包含此文字的藥物
                results = db.search_by_name(text, limit=3)

                for drug in results:
                    # 檢查是否已存在
                    if not any(m["id"] == drug["id"] for m in matched_drugs):
                        # 補充圖片資訊
                        images = db.get_drug_images(drug["id"])
                        matched_drugs.append(
                            {
                                "id": drug["id"],
                                "chinese_name": drug["chinese_name"],
                                "english_name": drug["english_name"],
                                "license_number": drug["license_number"],
                                "shape": drug["shape"],
                                "color": drug["color"],
                                "special_dosage_form": drug["special_dosage_form"],
                                "matched_text": text,
                                "ocr_confidence": f"{confidence * 100:.1f}%",
                                "images": images,
                            }
                        )

        return {
            "success": True,
            "method": "OCR",
            "detected_texts": all_detected_texts,
            "matched_drugs_count": len(matched_drugs),
            "matched_drugs": matched_drugs,
        }

    def recognize_single_drug_name(self, image_path: str) -> Dict:
        """
        辨識單一藥物名稱（藥袋、藥盒照片）

        Args:
            image_path: 圖片路徑

        Returns:
            辨識結果
        """
        # 提取文字
        texts = self.extract_text(image_path)

        if not texts:
            return {"success": False, "message": "未能識別文字"}

        # 取置信度最高的幾個文字
        top_texts = sorted(texts, key=lambda x: x[1], reverse=True)[:5]

        # 搜尋藥物
        all_matches = []

        with DrugDatabase(self.db_path) as db:
            for text, confidence in top_texts:
                results = db.search_by_name(text, limit=5)

                for drug in results:
                    # 計算綜合相似度（OCR 置信度 + 名稱匹配度）
                    name_match_score = self._calculate_name_similarity(
                        text, drug["chinese_name"]
                    )
                    overall_score = 0.6 * confidence + 0.4 * name_match_score

                    images = db.get_drug_images(drug["id"])

                    all_matches.append(
                        {
                            "id": drug["id"],
                            "chinese_name": drug["chinese_name"],
                            "english_name": drug["english_name"],
                            "license_number": drug["license_number"],
                            "shape": drug["shape"],
                            "color": drug["color"],
                            "matched_text": text,
                            "ocr_confidence": f"{confidence * 100:.1f}%",
                            "similarity": overall_score,
                            "similarity_percent": f"{overall_score * 100:.1f}%",
                            "images": images,
                        }
                    )

        # 去重並排序
        unique_matches = []
        seen_ids = set()

        for match in sorted(all_matches, key=lambda x: x["similarity"], reverse=True):
            if match["id"] not in seen_ids:
                unique_matches.append(match)
                seen_ids.add(match["id"])

        return {
            "success": True,
            "method": "OCR",
            "count": len(unique_matches),
            "data": unique_matches[:5],  # 返回前 5 個
        }

    def _calculate_name_similarity(self, text1: str, text2: str) -> float:
        """
        計算兩個字串的相似度（簡單版本）

        Args:
            text1: 字串 1
            text2: 字串 2

        Returns:
            相似度 (0-1)
        """
        if not text1 or not text2:
            return 0.0

        # 轉為小寫並移除空白
        t1 = text1.lower().replace(" ", "")
        t2 = text2.lower().replace(" ", "")

        # 子字串包含檢查
        if t1 in t2 or t2 in t1:
            return 0.9

        # 簡單字元重疊率
        set1 = set(t1)
        set2 = set(t2)

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0


def test_ocr():
    """測試 OCR 功能"""
    print("=" * 50)
    print("測試 PaddleOCR 藥單辨識")
    print("=" * 50)

    recognizer = DrugOCRRecognizer()

    if recognizer.ocr is None:
        print("❌ OCR 未初始化，請先安裝依賴：")
        print("   pip install paddleocr paddlepaddle")
        return

    # 尋找測試圖片
    test_images = list(Path("medicine_photos").glob("*.jpg"))[:1]

    if not test_images:
        print("⚠️  沒有測試圖片")
        return

    test_image = str(test_images[0])
    print(f"\n📸 測試圖片: {test_image}")
    print("-" * 50)

    # 測試 OCR
    result = recognizer.recognize_single_drug_name(test_image)

    if result["success"]:
        print(f"✅ 辨識成功，找到 {result['count']} 個匹配")
        for i, drug in enumerate(result["data"][:3], 1):
            print(f"\n第 {i} 名：")
            print(f"  藥物名稱：{drug['chinese_name']}")
            print(f"  匹配文字：{drug['matched_text']}")
            print(f"  相似度：{drug['similarity_percent']}")
    else:
        print(f"❌ 辨識失敗：{result.get('message', '未知錯誤')}")


if __name__ == "__main__":
    test_ocr()
