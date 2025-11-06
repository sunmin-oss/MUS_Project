"""
藥物圖片辨識模組
支援多種辨識方法：特徵比對、OCR 文字辨識
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sqlite3
import threading


class DrugImageRecognizer:
    """藥物圖片辨識器（特徵比對方法）"""

    def __init__(
        self, db_path: str = "drug_recognition.db", photo_dir: str = "medicine_photos"
    ):
        self.db_path = db_path
        self.photo_dir = Path(photo_dir)
        self._image_records: List[Dict[str, str]] = []
        self._metadata_loaded = False
        self._feature_cache: Dict[str, Tuple[np.ndarray, float, np.ndarray]] = (
            {}
        )  # 增加 LBP
        self._orb_cache: Dict[str, Optional[np.ndarray]] = {}
        self._features_loaded = False
        self._load_lock = threading.Lock()
        self._computed_count = 0
        self._orb = cv2.ORB_create(nfeatures=500)
        self._load_thread: Optional[threading.Thread] = threading.Thread(
            target=self._load_database_features, daemon=True
        )
        self._load_thread.start()

    def _load_image_metadata(self) -> None:
        """載入所有藥物圖片的資料列。"""
        if self._metadata_loaded:
            return

        with self._load_lock:
            if self._metadata_loaded:
                return

            conn = None
            try:
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
                rows = cursor.fetchall()
                self._image_records = [
                    {
                        "drug_id": row[0],
                        "chinese_name": row[1],
                        "english_name": row[2],
                        "license_number": row[3],
                        "shape": row[4],
                        "color": row[5],
                        "special_dosage_form": row[6],
                        "image_filename": row[7],
                    }
                    for row in rows
                ]
                self._metadata_loaded = True
            except Exception as exc:
                print(f"⚠️ 無法載入資料庫圖片清單: {exc}")
                self._image_records = []
            finally:
                try:
                    if conn:
                        conn.close()
                except Exception:
                    pass

    def _get_or_compute_features(
        self, record: Dict[str, str]
    ) -> Optional[Tuple[np.ndarray, float, np.ndarray]]:
        """取得或計算指定圖片的特徵 (顏色、形狀、LBP紋理)。"""

        filename = record["image_filename"]
        with self._load_lock:
            cached = self._feature_cache.get(filename)
        if cached is not None:
            return cached

        image_path = self.photo_dir / filename
        if not image_path.exists():
            return None

        db_img = self.preprocess_image(str(image_path), apply_denoise=False)
        if db_img is None:
            return None

        db_hist = self.extract_color_histogram(db_img)
        db_shape = self.extract_shape_features(db_img)
        db_lbp = self.extract_lbp_features(db_img)
        features = (db_hist, db_shape.get("circularity", 0.0), db_lbp)

        with self._load_lock:
            self._feature_cache[filename] = features
            self._computed_count = len(self._feature_cache)

        total = len(self._image_records)
        if total and self._computed_count % 200 == 0:
            print(f"📸 已計算 {self._computed_count}/{total} 張藥品圖片特徵")

        return features

    def _get_or_compute_orb(
        self, filename: str, image_path: Path
    ) -> Optional[np.ndarray]:
        """延遲計算指定圖片的 ORB 描述子並快取。"""

        with self._load_lock:
            if filename in self._orb_cache:
                return self._orb_cache[filename]

        if not image_path.exists():
            with self._load_lock:
                self._orb_cache[filename] = None
            return None

        db_img = self.preprocess_image(str(image_path), apply_denoise=False)
        if db_img is None:
            with self._load_lock:
                self._orb_cache[filename] = None
            return None

        descriptors = self.extract_orb_descriptors(db_img)

        with self._load_lock:
            self._orb_cache[filename] = descriptors

        return descriptors

    def _match_filters(
        self,
        record: Dict[str, str],
        filter_shape: Optional[str],
        filter_color: Optional[str],
    ) -> bool:
        """
        檢查藥物記錄是否符合形狀和顏色篩選條件

        Args:
            record: 藥物記錄字典
            filter_shape: 篩選形狀
            filter_color: 篩選顏色

        Returns:
            True 如果符合所有指定的篩選條件，否則 False
        """
        # 檢查形狀
        if filter_shape:
            drug_shape = record.get("shape", "")
            if not drug_shape or filter_shape not in drug_shape:
                return False

        # 檢查顏色
        if filter_color:
            drug_color = record.get("color", "")
            if not drug_color or filter_color not in drug_color:
                return False

        return True

    def _load_database_features(self) -> None:
        """背景載入圖片清單並預先計算少量特徵。"""

        self._load_image_metadata()

        total = len(self._image_records)
        preload_cap = min(50, total)
        loaded = 0

        if preload_cap:
            for record in self._image_records[:preload_cap]:
                if self._get_or_compute_features(record) is not None:
                    loaded += 1

        with self._load_lock:
            self._features_loaded = loaded >= total and total > 0

        if total:
            print(
                f"✅ 已預先載入 {loaded}/{total} 筆藥品圖片特徵（其餘將於查詢時動態計算）"
            )
        else:
            print("⚠️ 未在資料庫中找到可用的藥品圖片")

    def reload_feature_cache(self, async_load: bool = False) -> None:
        """重新整理快取，支援背景載入。"""

        def _reload():
            with self._load_lock:
                self._features_loaded = False
                self._feature_cache.clear()
                self._metadata_loaded = False
                self._computed_count = 0
            self._load_database_features()

        if async_load:
            threading.Thread(target=_reload, daemon=True).start()
        else:
            _reload()

    def preprocess_image(
        self, image_path: str, apply_denoise: bool = True
    ) -> Optional[np.ndarray]:
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

            # 降噪運算成本高，僅針對上傳圖片執行
            if apply_denoise:
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

    def extract_orb_descriptors(self, image: np.ndarray) -> Optional[np.ndarray]:
        """提取 ORB 特徵描述子以辨識藥錠刻印。"""

        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            keypoints, descriptors = self._orb.detectAndCompute(gray, None)
            if descriptors is None or len(descriptors) == 0:
                return None
            return descriptors
        except Exception as exc:
            print(f"ORB 特徵提取失敗: {exc}")
            return None

    def extract_lbp_features(
        self, image: np.ndarray, radius: int = 3, n_points: int = 24
    ) -> np.ndarray:
        """
        提取 LBP (Local Binary Pattern) 紋理特徵
        LBP 可以捕捉藥物表面的紋理、刻痕、光澤等細節

        Args:
            image: 圖片陣列
            radius: LBP 半徑 (預設 3)
            n_points: 採樣點數量 (預設 24)

        Returns:
            LBP 直方圖特徵向量
        """
        try:
            # 轉為灰階
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 套用高斯模糊減少雜訊
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            h, w = gray.shape
            # 使用更大的數據類型來避免溢出
            lbp_image = np.zeros_like(gray, dtype=np.int32)

            # 計算 LBP
            for i in range(radius, h - radius):
                for j in range(radius, w - radius):
                    center = float(gray[i, j])
                    binary_string = []

                    # 在圓形鄰域採樣
                    for k in range(n_points):
                        angle = 2 * np.pi * k / n_points
                        x = i + radius * np.cos(angle)
                        y = j + radius * np.sin(angle)

                        # 雙線性插值
                        x1, y1 = int(x), int(y)
                        x2, y2 = min(x1 + 1, h - 1), min(y1 + 1, w - 1)

                        if x2 >= h or y2 >= w or x1 < 0 or y1 < 0:
                            continue

                        dx, dy = x - x1, y - y1
                        pixel_value = (
                            float(gray[x1, y1]) * (1 - dx) * (1 - dy)
                            + float(gray[x2, y1]) * dx * (1 - dy)
                            + float(gray[x1, y2]) * (1 - dx) * dy
                            + float(gray[x2, y2]) * dx * dy
                        )

                        binary_string.append(1 if pixel_value >= center else 0)

                    # 轉換為 LBP 值 (限制在合理範圍)
                    if len(binary_string) == n_points:
                        lbp_value = sum(
                            [bit * (2**idx) for idx, bit in enumerate(binary_string)]
                        )
                        # 使用模運算確保值在合理範圍內
                        lbp_image[i, j] = lbp_value % 256

            # 計算 LBP 直方圖
            hist, _ = np.histogram(lbp_image.ravel(), bins=256, range=(0, 256))

            # 正規化
            hist = hist.astype(float)
            hist_sum = hist.sum()
            if hist_sum > 0:
                hist = hist / hist_sum

            return hist

        except Exception as e:
            print(f"LBP 特徵提取失敗: {e}")
            # 返回零向量
            return np.zeros(256)

    def extract_mark_features(self, mark_text: str) -> str:
        """
        提取並標準化刻痕特徵文字

        Args:
            mark_text: 藥物刻痕描述文字

        Returns:
            標準化的刻痕特徵字串
        """
        if not mark_text or mark_text == "無" or mark_text == "None":
            return ""

        # 移除空白和標點符號,轉為大寫
        import re

        mark_text = mark_text.upper()
        mark_text = re.sub(r"[^\w\s]", "", mark_text)
        mark_text = re.sub(r"\s+", "", mark_text)

        return mark_text

    def calculate_mark_similarity(self, mark1: str, mark2: str) -> float:
        """
        計算兩個刻痕描述的相似度

        Args:
            mark1: 第一個刻痕描述
            mark2: 第二個刻痕描述

        Returns:
            相似度分數 (0-1)
        """
        m1 = self.extract_mark_features(mark1)
        m2 = self.extract_mark_features(mark2)

        if not m1 or not m2:
            return 0.0

        if m1 == m2:
            return 1.0

        # 使用序列匹配計算相似度
        from difflib import SequenceMatcher

        matcher = SequenceMatcher(None, m1, m2)
        return matcher.ratio()

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

    def calculate_orb_similarity(
        self, descriptors1: Optional[np.ndarray], descriptors2: Optional[np.ndarray]
    ) -> float:
        """計算 ORB 描述子的相似度，值域 0-1。"""

        if descriptors1 is None or descriptors2 is None:
            return 0.0

        try:
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = matcher.knnMatch(descriptors1, descriptors2, k=2)
        except cv2.error as exc:
            print(f"ORB 比對失敗: {exc}")
            return 0.0

        good_matches = 0
        for pair in matches:
            if len(pair) < 2:
                continue
            m, n = pair
            if m.distance < 0.75 * n.distance:
                good_matches += 1

        max_possible = min(len(descriptors1), len(descriptors2))
        if max_possible == 0:
            return 0.0

        return good_matches / max_possible

    def calculate_lbp_similarity(self, lbp1: np.ndarray, lbp2: np.ndarray) -> float:
        """
        計算兩個 LBP 直方圖的相似度（使用卡方距離）

        Args:
            lbp1: 第一個 LBP 直方圖
            lbp2: 第二個 LBP 直方圖

        Returns:
            相似度分數 (0-1)
        """
        try:
            # 使用卡方距離
            chi_square = 0.0
            for i in range(len(lbp1)):
                if lbp1[i] + lbp2[i] > 0:
                    chi_square += ((lbp1[i] - lbp2[i]) ** 2) / (lbp1[i] + lbp2[i])

            # 轉換為相似度 (距離越小,相似度越高)
            # 使用指數函數將距離轉換為 0-1 範圍的相似度
            similarity = np.exp(-chi_square / 2)

            return float(max(0.0, min(1.0, similarity)))

        except Exception as e:
            print(f"LBP 相似度計算失敗: {e}")
            return 0.0

    def recognize_drug(
        self,
        uploaded_image_path: str,
        top_k: int = 5,
        filter_shape: Optional[str] = None,
        filter_color: Optional[str] = None,
    ) -> List[Dict]:
        """
        辨識上傳的藥物圖片

        Args:
            uploaded_image_path: 上傳圖片的路徑
            top_k: 返回前 K 個最相似的結果
            filter_shape: 篩選形狀 (選填)
            filter_color: 篩選顏色 (選填)

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
        uploaded_orb = self.extract_orb_descriptors(uploaded_img)
        uploaded_lbp = self.extract_lbp_features(uploaded_img)

        self._load_image_metadata()

        if not self._image_records:
            return []

        # 預先過濾符合形狀/顏色條件的藥物記錄
        filtered_records = self._image_records
        if filter_shape or filter_color:
            filtered_records = [
                record
                for record in self._image_records
                if self._match_filters(record, filter_shape, filter_color)
            ]
            print(
                f"📋 套用篩選條件後，剩餘 {len(filtered_records)}/{len(self._image_records)} 筆藥物"
            )

        if not filtered_records:
            print("⚠️  沒有符合篩選條件的藥物")
            return []

        # 獲取所有有圖片的藥物
        results = []

        for record in filtered_records:
            features = self._get_or_compute_features(record)
            if features is None:
                continue

            db_hist, db_circularity, db_lbp = features

            # 計算相似度
            color_similarity = self.calculate_similarity(uploaded_hist, db_hist)

            # 形狀相似度（簡單比較圓度）
            shape_similarity = 1 - abs(uploaded_shape["circularity"] - db_circularity)
            shape_similarity = max(0.0, shape_similarity)

            # LBP 紋理相似度
            lbp_similarity = self.calculate_lbp_similarity(uploaded_lbp, db_lbp)

            # ORB 刻印相似度（延遲計算）
            orb_similarity = 0.0
            if uploaded_orb is not None and color_similarity >= 0.3:
                image_path = self.photo_dir / record["image_filename"]
                db_orb = self._get_or_compute_orb(record["image_filename"], image_path)
                orb_similarity = self.calculate_orb_similarity(uploaded_orb, db_orb)

            # 刻痕文字相似度
            mark_similarity = 0.0
            if record.get("mark"):
                # 這裡暫時使用 0，因為上傳圖片沒有刻痕文字資訊
                # 如果未來加入 OCR 識別刻痕文字，可以在這裡比對
                mark_similarity = 0.0

            # 綜合相似度（調整權重）
            # 顏色 0.25, 形狀 0.15, LBP紋理 0.30, ORB刻印 0.30
            overall_similarity = (
                0.25 * color_similarity
                + 0.15 * shape_similarity
                + 0.30 * lbp_similarity
                + 0.30 * orb_similarity
            )

            results.append(
                {
                    **record,
                    "similarity": float(overall_similarity),
                    "similarity_percent": f"{overall_similarity * 100:.1f}%",
                    "details": {
                        "color": f"{color_similarity * 100:.1f}%",
                        "shape": f"{shape_similarity * 100:.1f}%",
                        "texture": f"{lbp_similarity * 100:.1f}%",
                        "imprint": f"{orb_similarity * 100:.1f}%",
                    },
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
