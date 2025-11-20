"""
============================================================================
藥物辨識系統 - 影像辨識模組 (image_recognition.py)
============================================================================

【檔案功能】
此模組是系統的核心辨識引擎，使用 OpenCV 進行藥物圖片的特徵提取與比對。

【主要功能】
1. 圖片預處理
   - 調整圖片大小為標準尺寸 (300x300)
   - CLAHE 對比度增強
   - 降噪處理

2. 特徵提取 (四大特徵維度)
   - 顏色特徵 (權重 40%): HSV 色彩直方圖 (18×8×8 bins)
   - 形狀特徵 (權重 30%): 圓度、長寬比、輪廓分析
   - 紋理特徵 (權重 20%): LBP (Local Binary Pattern) 紋理特徵
   - 印字特徵 (權重 10%): ORB 特徵點偵測 (500 個特徵點)

3. 相似度計算
   - 顏色: 直方圖相關係數 (Histogram Correlation)
   - 形狀: 歐式距離計算
   - 紋理: LBP 直方圖比對
   - 印字: ORB 特徵點匹配

4. 智慧過濾與懲罰機制
   - 顏色相似度 <35% → 0.3x 懲罰, <50% → 0.6x 懲罰
   - 形狀相似度 <30% → 0.5x 懲罰, <40% → 0.7x 懲罰
   - 最低相似度門檻: 15% (過濾低品質結果)

5. 顏色自動推論
   - 支援 11 種顏色: 紅、橙、黃、綠、藍、紫、粉紅、褐、白、灰、黑
   - 使用 HSV 色彩空間精確判斷

【演算法優化】
- 多層次背景遮罩策略 (過濾白色背景)
- 自適應二值化處理 (處理光照不均)
- 形態學操作 (閉運算填補孔洞、開運算去除雜訊)
- 特徵快取機制 (加速重複查詢)
- 多執行緒預載入 (背景載入資料庫特徵)

【辨識流程】
1. 上傳圖片 → 預處理 → 特徵提取
2. 與資料庫中 4775+ 張藥物圖片比對
3. 計算加權相似度分數
4. 套用智慧過濾與懲罰機制
5. 回傳前 10 名最相似的藥物

【效能表現】
- 預載入前 50 筆熱門藥物特徵
- 平均辨識時間: 2-5 秒
- 目標準確率: >70%

【使用範例】
    recognizer = DrugImageRecognizer()
    results = recognizer.recognize_drug("uploaded_image.jpg")

    for result in results:
        print(f"{result['chinese_name']}: {result['similarity']:.2f}%")

【注意事項】
- 圖片建議: 白色背景、藥物置中、清晰照明
- 形狀篩選使用精確匹配 (圓形 ≠ 橢圓形)
- 顏色篩選使用模糊匹配 (黃 可匹配 黃色)

【作者】MUS_Project 團隊
【日期】2024-2025
============================================================================
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import sqlite3
import threading


class DrugImageRecognizer:
    """
    藥物圖片辨識器 (基於特徵比對方法)

    核心技術:
    - 多執行緒特徵預載入，加快首次辨識速度
    - 特徵快取機制，避免重複計算
    - 支援形狀、顏色篩選條件
    - 進度回報與取消機制

    辨識流程:
    1. 載入資料庫中所有藥物圖片的中繼資料
    2. 背景執行緒預先計算資料庫圖片的特徵 (顏色、形狀、紋理)
    3. 使用者上傳圖片後，提取上傳圖片的特徵
    4. 逐一比對資料庫圖片，計算相似度分數
    5. 回傳 Top-K 最相似的藥物候選

    效能優化:
    - 特徵預載入: 首次辨識需等待約 30-60 秒，之後即時響應
    - 特徵快取: 已計算的特徵存於記憶體，避免重複運算
    - ORB 快取: 刻痕特徵單獨快取，降低記憶體使用
    """

    def __init__(
        self, db_path: str = "drug_recognition.db", photo_dir: str = "medicine_photos"
    ):
        """
        初始化藥物圖片辨識器

        參數:
            db_path (str): SQLite 資料庫路徑，預設 "drug_recognition.db"
            photo_dir (str): 藥物圖片資料夾路徑，預設 "medicine_photos"

        說明:
        - 建構完成後會自動啟動背景執行緒預載特徵
        - 預載期間仍可進行辨識，但速度較慢
        - 建議在系統啟動時初始化此物件
        """
        self.db_path = db_path
        self.photo_dir = Path(photo_dir)
        self._image_records: List[Dict[str, str]] = []  # 藥物圖片中繼資料
        self._metadata_loaded = False  # 中繼資料是否已載入
        # 特徵快取: filename -> (color_hist, shape_dict, lbp_hist)
        self._feature_cache: Dict[
            str, Tuple[np.ndarray, Dict[str, float], np.ndarray]
        ] = {}
        self._orb_cache: Dict[str, Optional[np.ndarray]] = {}  # ORB 刻痕特徵快取
        self._features_loaded = False  # 特徵是否已全部預載
        self._load_lock = threading.Lock()  # 執行緒鎖，避免重複載入
        self._computed_count = 0  # 已計算特徵的圖片數量
        self._orb = cv2.ORB_create(nfeatures=500)  # ORB 特徵偵測器 (刻痕辨識用)
        # 啟動背景執行緒預載特徵
        self._load_thread: Optional[threading.Thread] = threading.Thread(
            target=self._load_database_features, daemon=True
        )
        self._load_thread.start()

    def _load_image_metadata(self) -> None:
        """
        載入所有藥物圖片的中繼資料 (從資料庫)

        功能:
        - 讀取 drugs 和 drug_images 資料表的關聯資料
        - 建立藥物 ID、名稱、圖片檔名的對應清單
        - 使用執行緒鎖確保只載入一次

        載入資料包含:
        - drug_id: 藥物 ID
        - chinese_name, english_name: 中英文名稱
        - license_number: 許可證字號
        - shape, color: 外觀特徵
        - special_dosage_form: 特殊劑型
        - image_filename: 圖片檔名

        說明:
        - 此方法會在背景執行緒中自動呼叫
        - 載入失敗時會印出警告訊息，但不會中斷程式執行
        """
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
    ) -> Optional[Tuple[np.ndarray, Dict[str, float], np.ndarray]]:
        """取得或計算指定圖片的特徵 (顏色直方圖、形狀字典、LBP紋理)。"""

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
        # 儲存完整形狀特徵（circularity 和 aspect_ratio）
        features = (db_hist, db_shape, db_lbp)

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

        注意：形狀使用精確匹配，顏色使用模糊匹配

        Args:
            record: 藥物記錄字典
            filter_shape: 篩選形狀（精確匹配）
            filter_color: 篩選顏色（模糊匹配）

        Returns:
            True 如果符合所有指定的篩選條件，否則 False
        """
        # 檢查形狀（精確匹配，避免「圓形」匹配到「橢圓形」）
        if filter_shape:
            drug_shape = record.get("shape", "")
            if not drug_shape or drug_shape != filter_shape:
                return False

        # 檢查顏色（模糊匹配，允許「黃」匹配「黃色」）
        if filter_color:
            drug_color = record.get("color", "")
            if not drug_color or filter_color not in drug_color:
                return False

        return True

    def _infer_color_labels(self, image: np.ndarray) -> List[str]:
        """
        由圖片推估顏色標籤（中文），回傳候選標籤列表，用於縮小比對範圍。

        可能回傳：['白', '白色']、['紅', '紅色']、['粉', '粉紅', '粉紅色']、['黃', '黃色']、
                 ['綠', '綠色']、['藍', '藍色']、['紫', '紫色']、['橙', '橘', '橙色', '橘色']、
                 ['黑', '黑色']、['灰', '灰色']、['棕', '咖啡', '棕色', '咖啡色']
        """
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h = hsv[:, :, 0].astype(np.float32)
            s = hsv[:, :, 1].astype(np.float32)
            v = hsv[:, :, 2].astype(np.float32)

            mean_s = float(np.mean(s))
            mean_v = float(np.mean(v))
            mean_h = float(np.mean(h))  # 0~180

            # 低飽和度：黑/白/灰
            if mean_s < 30:
                if mean_v > 180:
                    return ["白", "白色"]
                elif mean_v < 60:
                    return ["黑", "黑色"]
                else:
                    return ["灰", "灰色"]

            # 粉紅色/粉色：紅色系但飽和度較低、亮度較高
            if (mean_h <= 10 or mean_h >= 160) and 30 <= mean_s < 100 and mean_v > 150:
                return ["粉", "粉紅", "粉紅色", "粉色"]

            # 以 Hue 判斷色調
            if mean_h <= 10 or mean_h >= 160:
                return ["紅", "紅色", "粉", "粉紅"]  # 紅色也包含粉紅可能
            if 11 <= mean_h <= 25:
                return ["橙", "橘", "橙色", "橘色"]
            if 26 <= mean_h <= 34:
                return ["黃", "黃色"]
            if 35 <= mean_h <= 85:
                return ["綠", "綠色"]
            if 86 <= mean_h <= 125:
                return ["藍", "藍色"]
            if 126 <= mean_h <= 159:
                return ["紫", "紫色"]

            # 其他色調視為棕/咖啡
            return ["棕", "咖啡", "棕色", "咖啡色"]
        except Exception:
            return []

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
        預處理圖片：調整大小、去噪、增強對比度

        Args:
            image_path: 圖片路徑
            apply_denoise: 是否應用降噪（上傳圖片建議開啟）

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

            # 增強對比度（CLAHE - Contrast Limited Adaptive Histogram Equalization）
            # 將 BGR 轉為 LAB 色彩空間，只對亮度通道做直方圖均衡化
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            img = cv2.merge([l, a, b])
            img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)

            # 降噪運算成本高，僅針對上傳圖片執行
            if apply_denoise:
                img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

            return img
        except Exception as e:
            print(f"圖片預處理失敗: {e}")
            return None

    def extract_color_histogram(self, image: np.ndarray) -> np.ndarray:
        """
        提取顏色直方圖特徵（優化版：專注於藥物主體，增強顏色區分度）

        Args:
            image: 圖片陣列

        Returns:
            顏色直方圖特徵向量
        """
        # 轉換到 HSV 色彩空間
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 多層次遮罩策略
        # 1. 基本遮罩：過濾純白背景
        mask1 = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 250]))

        # 2. 排除純白區域（V > 245 且 S < 20）
        white_mask = cv2.inRange(hsv, np.array([0, 0, 245]), np.array([180, 20, 255]))
        mask = cv2.bitwise_and(mask1, cv2.bitwise_not(white_mask))

        # 如果有效區域太小（< 10%），使用整張圖
        valid_pixels = cv2.countNonZero(mask)
        total_pixels = image.shape[0] * image.shape[1]
        if valid_pixels < total_pixels * 0.1:
            mask = None

        # 使用更細緻的分箱來提高顏色區分度
        # H: 18 bins (每 10 度), S: 8 bins, V: 8 bins
        hist = cv2.calcHist(
            [hsv],
            [0, 1, 2],
            mask,
            [18, 8, 8],  # 增加色相分箱以提高顏色敏感度
            [0, 180, 0, 256, 0, 256],
        )

        # 正規化
        hist = cv2.normalize(hist, hist).flatten()

        return hist

    def extract_shape_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        提取形狀特徵（優化版：更好處理帶孔藥物）

        Args:
            image: 圖片陣列

        Returns:
            形狀特徵字典
        """
        # 轉為灰階
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 高斯模糊減少雜訊
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # 自適應二值化（更好處理光照不均）
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # 形態學操作：閉運算填補小孔洞，開運算去除雜訊
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # 尋找輪廓
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return {"area": 0, "perimeter": 0, "circularity": 0, "aspect_ratio": 1.0}

        # 選擇最大的輪廓（假設為藥物主體）
        contour = max(contours, key=cv2.contourArea)

        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        # 計算圓度（4π × 面積 / 周長²）
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
        else:
            circularity = 0

        # 計算長寬比（用於區分圓形、橢圓、長條形）
        rect = cv2.minAreaRect(contour)
        width, height = rect[1]
        if width > 0 and height > 0:
            aspect_ratio = max(width, height) / min(width, height)
        else:
            aspect_ratio = 1.0

        return {
            "area": float(area),
            "perimeter": float(perimeter),
            "circularity": float(circularity),
            "aspect_ratio": float(aspect_ratio),
        }

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
        self, image: np.ndarray, radius: int = 1, n_points: int = 8
    ) -> np.ndarray:
        """
        提取 LBP (Local Binary Pattern) 紋理特徵（高速向量化版本）

        說明：
        - 將灰階圖縮放至 128x128，使用 8 鄰域、半徑 1 的經典 LBP。
        - 以 numpy 位元運算計算，不使用巢狀 Python 迴圈，大幅降低延遲。

        Args:
            image: 圖片陣列
            radius: LBP 半徑（僅支援 1，用於快速運算）
            n_points: 鄰域點數（僅支援 8）

        Returns:
            長度 256 的 LBP 直方圖（已正規化）
        """
        try:
            # 轉為灰階並縮小尺寸以降低運算量
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (128, 128), interpolation=cv2.INTER_AREA)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)

            if radius != 1 or n_points != 8:
                # 為保持速度與穩定性，暫時僅支援 (radius=1, n_points=8)
                radius = 1
                n_points = 8

            # 內部區域（避免邊界）
            c = gray[1:-1, 1:-1]
            codes = np.zeros_like(c, dtype=np.uint8)

            # 8 個鄰居位移（順時針）
            neighbors = [
                gray[0:-2, 0:-2],  # (-1,-1)
                gray[0:-2, 1:-1],  # (-1, 0)
                gray[0:-2, 2:],  # (-1,+1)
                gray[1:-1, 2:],  # ( 0,+1)
                gray[2:, 2:],  # (+1,+1)
                gray[2:, 1:-1],  # (+1, 0)
                gray[2:, 0:-2],  # (+1,-1)
                gray[1:-1, 0:-2],  # ( 0,-1)
            ]

            for bit, n in enumerate(neighbors):
                codes |= (n >= c).astype(np.uint8) << bit

            # 計算直方圖並正規化
            hist, _ = np.histogram(codes.ravel(), bins=256, range=(0, 256))
            hist = hist.astype(np.float32)
            s = hist.sum()
            if s > 0:
                hist /= s

            return hist

        except Exception as e:
            print(f"LBP 特徵提取失敗: {e}")
            return np.zeros(256, dtype=np.float32)

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
        hooks: Optional[Dict[str, Any]] = None,
    ) -> List[Dict]:
        """
        辨識上傳的藥物圖片 (主要辨識方法)

        辨識流程:
        1. 載入並預處理上傳的圖片
        2. 提取上傳圖片的 4 種特徵 (顏色、形狀、紋理、刻痕)
        3. 根據篩選條件或自動顏色推估縮小候選範圍
        4. 逐一比對資料庫中的藥物圖片
        5. 計算綜合相似度分數 (4 種特徵加權平均)
        6. 套用懲罰機制 (形狀/顏色不符會扣分)
        7. 回傳 Top-K 最相似的藥物候選

        特徵權重分配:
        - 顏色相似度: 40% (主要篩選依據)
        - 形狀相似度: 30% (圓度 70% + 長寬比 30%)
        - 紋理相似度: 20% (LBP 特徵)
        - 刻痕相似度: 10% (ORB 特徵點比對)

        自動優化機制:
        - 自動顏色推估: 未指定篩選條件時，從圖片推估顏色並縮小候選範圍
        - 延遲計算: ORB 刻痕特徵僅在顏色相似度 >= 0.3 時才計算，節省運算
        - 懲罰機制: 形狀或顏色完全不符時，相似度扣減 30-50%

        參數:
            uploaded_image_path (str): 上傳圖片的檔案路徑
            top_k (int): 回傳前 K 名候選，預設 5
            filter_shape (str): 形狀篩選條件 (選填，例如: "圓形")
            filter_color (str): 顏色篩選條件 (選填，例如: "白色")
            hooks (dict): 進度回報與取消機制的 callback 函數
                - on_progress(done, total): 回報進度
                - is_cancelled(): 檢查是否取消

        回傳:
            List[Dict]: Top-K 辨識結果，每筆包含:
                - drug_id: 藥物 ID
                - chinese_name: 中文名稱
                - similarity: 相似度分數 (0-1)
                - similarity_percent: 相似度百分比
                - color_similarity, shape_similarity, ...: 各項特徵相似度

        範例:
            results = recognizer.recognize_drug(
                "uploads/pill.jpg",
                top_k=10,
                filter_color="白色"
            )

        注意:
        - 首次辨識需等待背景執行緒完成特徵預載入 (約 30-60 秒)
        - 後續辨識即時響應 (通常 < 1 秒)
        - 篩選條件會顯著影響結果準確度，建議提供準確的形狀/顏色
        """
        import time

        t0 = time.time()

        # 解包 hooks (進度回報與取消機制)
        on_progress = None
        is_cancelled = None
        if isinstance(hooks, dict):
            on_progress = hooks.get("on_progress")
            is_cancelled = hooks.get("is_cancelled")
            if not callable(on_progress):
                on_progress = None
            if not callable(is_cancelled):
                is_cancelled = None

        # 預處理上傳的圖片 (調整大小、去噪等)
        uploaded_img = self.preprocess_image(uploaded_image_path)
        if uploaded_img is None:
            return []

        # 提取上傳圖片的 4 種特徵
        uploaded_hist = self.extract_color_histogram(uploaded_img)  # 顏色直方圖
        uploaded_shape = self.extract_shape_features(uploaded_img)  # 形狀特徵
        uploaded_orb = self.extract_orb_descriptors(uploaded_img)  # ORB 刻痕特徵
        uploaded_lbp = self.extract_lbp_features(uploaded_img)  # LBP 紋理特徵

        # 載入資料庫藥物圖片的中繼資料
        self._load_image_metadata()

        if not self._image_records:
            return []

        # 預先過濾符合形狀/顏色條件的藥物記錄
        filtered_records = self._image_records
        if filter_shape or filter_color:
            # 使用者指定篩選條件
            filtered_records = [
                record
                for record in self._image_records
                if self._match_filters(record, filter_shape, filter_color)
            ]
            print(
                f"📋 套用篩選條件後，剩餘 {len(filtered_records)}/{len(self._image_records)} 筆藥物"
            )
        else:
            # 未指定篩選時，依據圖片自動推估顏色，縮小搜尋空間
            auto_colors = self._infer_color_labels(uploaded_img)
            if auto_colors:
                filtered_records = [
                    r
                    for r in self._image_records
                    if any(lbl in (r.get("color") or "") for lbl in auto_colors)
                ]
                print(
                    f"🎯 自動推估顏色 {auto_colors}，候選縮小為 {len(filtered_records)}/{len(self._image_records)} 筆"
                )

        if not filtered_records:
            print("⚠️  沒有符合篩選條件的藥物")
            return []

        # 獲取所有有圖片的藥物
        results = []
        total_candidates = len(filtered_records)
        if on_progress:
            try:
                on_progress(0, total_candidates)
            except Exception:
                pass

        for idx, record in enumerate(filtered_records, start=1):
            if is_cancelled and is_cancelled():
                print("🛑 收到取消信號，提前結束比對")
                break
            features = self._get_or_compute_features(record)
            if features is None:
                continue

            db_hist, db_shape, db_lbp = features

            # 計算相似度
            color_similarity = self.calculate_similarity(uploaded_hist, db_hist)

            # 形狀相似度（綜合圓度和長寬比）
            circularity_sim = 1 - abs(
                uploaded_shape["circularity"] - db_shape.get("circularity", 0.0)
            )
            circularity_sim = max(0.0, circularity_sim)

            aspect_ratio_sim = (
                1
                - abs(
                    uploaded_shape["aspect_ratio"] - db_shape.get("aspect_ratio", 1.0)
                )
                / 2.0
            )
            aspect_ratio_sim = max(0.0, min(1.0, aspect_ratio_sim))

            # 綜合形狀相似度（圓度70% + 長寬比30%）
            shape_similarity = 0.7 * circularity_sim + 0.3 * aspect_ratio_sim

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

            # 綜合相似度（優化權重配置）
            # 策略：顏色和形狀作為主要篩選,紋理和刻印作為細節辨識
            # 顏色 0.40（大幅提高），形狀 0.30（提高），LBP紋理 0.20（降低），ORB刻印 0.10（降低）

            # 更嚴格的懲罰機制
            # 顏色相似度低於 50% 給予重度懲罰
            if color_similarity < 0.35:
                color_penalty = 0.3  # 大幅降低
            elif color_similarity < 0.5:
                color_penalty = 0.6
            else:
                color_penalty = 1.0

            # 形狀相似度低於 40% 給予懲罰
            if shape_similarity < 0.3:
                shape_penalty = 0.5
            elif shape_similarity < 0.4:
                shape_penalty = 0.7
            else:
                shape_penalty = 1.0

            overall_similarity = (
                (
                    0.40 * color_similarity
                    + 0.30 * shape_similarity
                    + 0.20 * lbp_similarity
                    + 0.10 * orb_similarity
                )
                * color_penalty
                * shape_penalty
            )

            # 過濾掉相似度太低的結果（低於 15% 直接不列入）
            if overall_similarity < 0.15:
                continue

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

            # 避免單次請求沒有回應太久，對大型資料集每處理 200 筆就打印一次進度
            if idx % 200 == 0:
                elapsed = time.time() - t0
                print(f"⏱️ 已比對 {idx} 筆，耗時 {elapsed:.1f}s")
            if on_progress:
                try:
                    on_progress(idx, total_candidates)
                except Exception:
                    pass

        # 按相似度排序並返回前 K 個
        results.sort(key=lambda x: x["similarity"], reverse=True)

        elapsed = time.time() - t0
        print(
            f"✅ 比對完成：候選 {len(filtered_records)} → 取前 {top_k}，總耗時 {elapsed:.2f}s"
        )
        if on_progress:
            try:
                on_progress(total_candidates, total_candidates)
            except Exception:
                pass

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
