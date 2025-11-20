"""
============================================================================
藥物辨識系統 - 資料庫查詢模組 (database_query.py)
============================================================================

【檔案功能】
此模組負責所有與藥物資料庫的互動操作，提供完整的 CRUD (Create, Read, Update, Delete) 功能。

【主要功能】
1. 藥物資料查詢
   - 根據藥物 ID 查詢詳細資訊
   - 根據藥物名稱搜尋 (支援模糊搜尋與字形變體)
   - 根據外觀特徵搜尋 (顏色、形狀)

2. 圖片管理
   - 取得藥物對應的所有圖片
   - 更新圖片路徑資訊

3. 資料統計
   - 統計資料庫中的藥物總數
   - 統計圖片數量

4. 模糊搜尋增強
   - 支援字形變體 (例如: 靈⇄林, 匹⇄必, 斯⇄思)
   - 自動生成多種搜尋變體以提高搜尋準確度

【資料庫結構】
- drugs 資料表: 儲存藥物詳細資訊 (24 個欄位)
- drug_images 資料表: 儲存藥物圖片資訊 (支援一藥多圖)

【使用範例】
    db = DrugDatabase("drug_recognition.db")
    db.connect()

    # 搜尋藥物
    results = db.search_by_name("普拿疼")

    # 取得藥物詳細資訊
    drug = db.get_drug_by_id(1)

    db.close()

【注意事項】
- 使用 SQLite 資料庫，單一檔案儲存
- 支援繁體中文搜尋
- 形狀篩選使用精確匹配，顏色篩選使用模糊匹配

【作者】MUS_Project 團隊
【日期】2024-2025
============================================================================
"""

import sqlite3
import os
from typing import List, Dict, Optional


class DrugDatabase:
    """
    藥物資料庫查詢類別

    功能:
    - 提供資料庫連線管理 (Context Manager 模式)
    - 實作各種藥物查詢方法 (名稱、特徵、ID)
    - 支援模糊搜尋與同音字/異體字辨識
    - 管理藥物與圖片的關聯資料

    使用方式:
        with DrugDatabase() as db:
            results = db.search_by_name("阿斯匹靈")
    """

    def __init__(self, db_file: str = "drug_recognition.db"):
        """
        初始化資料庫連線物件

        參數:
            db_file (str): SQLite 資料庫檔案路徑，預設 "drug_recognition.db"
        """
        self.db_file = db_file
        self.conn = None

    def connect(self):
        """
        建立資料庫連接

        說明:
        - 使用 sqlite3.Row 作為 row_factory，讓查詢結果可像字典般存取
        - 例如: row['chinese_name'] 而非 row[0]
        """
        if not self.conn:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # 讓結果可以像字典一樣訪問

    def close(self):
        """
        關閉資料庫連接，釋放資源
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """
        Context Manager 入口，自動建立連線

        使用方式:
            with DrugDatabase() as db:
                # 自動呼叫 connect()
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context Manager 出口，自動關閉連線

        說明:
        - 無論是否發生例外，都會確保連線被關閉
        - 防止資料庫鎖定或資源洩漏
        """
        self.close()

    # ===== 名稱搜索功能 =====

    def _normalize_search_query(self, query: str) -> List[str]:
        """
        正規化搜尋關鍵字，產生多個可能的字形變體

        功能:
        - 處理常見的同音字、異體字問題
        - 例如: "阿斯匹靈" → ["阿斯匹靈", "阿斯匹林", "阿思匹靈"...]
        - 提高搜尋成功率，避免因字形差異找不到藥物

        參數:
            query (str): 原始搜尋關鍵字

        回傳:
            List[str]: 包含原字和變體的關鍵字列表 (最多 10 個)

        範例:
            _normalize_search_query("阿斯匹靈")
            → ["阿斯匹靈", "阿斯匹林", "阿思匹靈", ...]
        """
        # 常見同音字/異體字對照表
        char_variants = {
            "靈": ["林", "霖", "琳"],
            "林": ["靈", "霖", "琳"],
            "匹": ["必", "比"],
            "必": ["匹", "比"],
            "斯": ["思", "絲"],
            "思": ["斯", "絲"],
            "克": ["剋", "刻"],
            "剋": ["克", "刻"],
            "服": ["複", "復"],
            "複": ["服", "復"],
            "寧": ["凝", "擰"],
            "凝": ["寧", "擰"],
            "痛": ["通", "桐"],
            "通": ["痛", "桐"],
            "炎": ["煙", "研"],
            "煙": ["炎", "研"],
            "咳": ["刻", "課"],
            "刻": ["咳", "課"],
        }

        queries = [query]  # 原始查詢

        # 產生變體
        for i, char in enumerate(query):
            if char in char_variants:
                new_queries = []
                for variant in char_variants[char]:
                    variant_query = query[:i] + variant + query[i + 1 :]
                    if variant_query not in queries:
                        new_queries.append(variant_query)
                queries.extend(new_queries[:3])  # 限制每個字最多3個變體

        return queries[:10]  # 限制總變體數量，避免查詢過慢

    def search_by_name(self, query: str, limit: int = 20) -> List[Dict]:
        """
        根據藥物名稱搜索 (增強型模糊搜索，支援同音字/異體字)

        功能:
        - 搜尋中文名稱或英文名稱
        - 自動處理字形變體 (例如: 靈⇄林)
        - 使用 LIKE 模糊比對，支援部分匹配
        - 依藥物 ID 排序，確保結果穩定

        參數:
            query (str): 搜索關鍵字 (中文或英文)
            limit (int): 返回結果數量限制，預設 20

        回傳:
            List[Dict]: 符合條件的藥物列表，每個藥物包含所有資料庫欄位

        範例:
            search_by_name("普拿疼", limit=10)
            search_by_name("aspirin", limit=5)
        """
        cursor = self.conn.cursor()

        # 產生多個搜尋變體 (處理同音字/異體字)
        search_variants = self._normalize_search_query(query)

        # 建立 WHERE 條件
        where_conditions = []
        params = []

        for variant in search_variants:
            where_conditions.append("d.chinese_name LIKE ?")
            where_conditions.append("d.english_name LIKE ?")
            params.extend([f"%{variant}%", f"%{variant}%"])

        # 建立 ORDER BY 條件 (完全匹配優先)
        order_conditions = []
        order_params = []
        for variant in search_variants:
            order_conditions.append("WHEN d.chinese_name LIKE ? THEN 1")
            order_conditions.append("WHEN d.english_name LIKE ? THEN 2")
            order_params.extend([f"{variant}%", f"{variant}%"])

        sql = f"""
            SELECT 
                d.id,
                d.license_number,
                d.chinese_name,
                d.english_name,
                d.shape,
                d.color,
                d.special_dosage_form,
                COUNT(di.id) as image_count
            FROM drugs d
            LEFT JOIN drug_images di ON d.id = di.drug_id
            WHERE 
                {' OR '.join(where_conditions)}
            GROUP BY d.id
            ORDER BY 
                CASE 
                    {' '.join(order_conditions)}
                    ELSE 3
                END,
                d.chinese_name
            LIMIT ?
        """

        all_params = params + order_params + [limit]
        cursor.execute(sql, all_params)

        return [dict(row) for row in cursor.fetchall()]

    def search_by_features(
        self, shape: str = None, color: str = None, label: str = None, limit: int = 20
    ) -> List[Dict]:
        """
        根據藥物外觀特徵搜索

        功能:
        - 形狀使用精確匹配 (避免"圓形"誤配到"橢圓形")
        - 顏色使用模糊匹配 (例如: "黃"可匹配"黃色"、"淡黃色")
        - 標記可搜尋正面或背面標註
        - 支援多條件組合查詢

        參數:
            shape (str): 形狀，精確匹配 (例如: "圓形", "橢圓形", "方形")
            color (str): 顏色，模糊匹配 (例如: "黃", "黃色")
            label (str): 標註 (搜尋 label_front 或 label_back 欄位)
            limit (int): 返回結果數量限制，預設 20

        回傳:
            List[Dict]: 符合條件的藥物列表

        範例:
            search_by_features(shape="圓形", color="白")
            search_by_features(color="紅", label="A")

        注意:
        - 形狀必須完全匹配，建議提供準確的形狀名稱
        - 顏色支援部分匹配，輸入"黃"即可找到包含"黃"的所有顏色
        """
        cursor = self.conn.cursor()

        conditions = []
        params = []

        if shape:
            # 形狀使用精確匹配，避免「圓形」匹配到「橢圓形」
            conditions.append("d.shape = ?")
            params.append(shape)

        if color:
            # 顏色使用模糊匹配，提高搜尋彈性
            conditions.append("d.color LIKE ?")
            params.append(f"%{color}%")

        if label:
            # 標記可能在正面或背面，兩者都搜尋
            conditions.append("(d.label_front LIKE ? OR d.label_back LIKE ?)")
            params.extend([f"%{label}%", f"%{label}%"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)

        cursor.execute(
            f"""
            SELECT 
                d.id,
                d.license_number,
                d.chinese_name,
                d.english_name,
                d.shape,
                d.color,
                d.mark,
                d.label_front,
                d.label_back,
                COUNT(di.id) as image_count
            FROM drugs d
            LEFT JOIN drug_images di ON d.id = di.drug_id
            WHERE {where_clause}
            GROUP BY d.id
            ORDER BY d.chinese_name
            LIMIT ?
        """,
            params,
        )

        return [dict(row) for row in cursor.fetchall()]

    # ===== 圖片相關查詢 =====

    def get_drug_images(self, drug_id: int) -> List[Dict]:
        """
        獲取特定藥物的所有圖片

        Args:
            drug_id: 藥物 ID

        Returns:
            圖片列表
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT 
                id,
                image_filename,
                image_path,
                image_order,
                feature_vector
            FROM drug_images
            WHERE drug_id = ?
            ORDER BY image_order
        """,
            (drug_id,),
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_all_drug_images(self) -> List[Dict]:
        """
        獲取所有藥物圖片（用於 AI 模型訓練或批量比對）

        Returns:
            所有圖片列表，包含關聯的藥物資訊
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT 
                di.id,
                di.image_filename,
                di.image_path,
                di.image_order,
                di.feature_vector,
                d.id as drug_id,
                d.license_number,
                d.chinese_name,
                d.english_name,
                d.shape,
                d.color
            FROM drug_images di
            JOIN drugs d ON di.drug_id = d.id
            ORDER BY d.id, di.image_order
        """
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_drug_with_images(self, drug_id: int) -> Optional[Dict]:
        """
        獲取藥物完整資訊（包含所有圖片）

        Args:
            drug_id: 藥物 ID

        Returns:
            藥物完整資訊字典
        """
        cursor = self.conn.cursor()

        # 獲取藥物基本資訊
        cursor.execute(
            """
            SELECT * FROM drugs WHERE id = ?
        """,
            (drug_id,),
        )

        result = cursor.fetchone()
        if not result:
            return None

        drug = dict(result)

        # 獲取圖片
        drug["images"] = self.get_drug_images(drug_id)

        return drug

    def get_drug(self, drug_id: int) -> Optional[Dict]:
        """取得單一藥物完整資訊（包含臨床資訊，不含圖片）。"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 
                id,
                license_number,
                chinese_name,
                english_name,
                shape,
                color,
                mark,
                size,
                special_dosage_form,
                special_odor,
                label_front,
                label_back,
                indications,
                dosage,
                side_effects,
                contraindications,
                precautions,
                ingredient,
                category,
                manufacturer,
                storage_conditions,
                expiry_info,
                created_at,
                updated_at
            FROM drugs
            WHERE id = ?
        """,
            (drug_id,),
        )

        result = cursor.fetchone()
        return dict(result) if result else None

    # ===== AI 模型特徵向量相關 =====

    def update_image_features(self, image_id: int, feature_vector: List[float]):
        """
        更新圖片的特徵向量（從 AI 模型提取的特徵）

        Args:
            image_id: 圖片 ID
            feature_vector: 特徵向量（列表）
        """
        cursor = self.conn.cursor()

        import json

        cursor.execute(
            """
            UPDATE drug_images
            SET feature_vector = ?
            WHERE id = ?
        """,
            (json.dumps(feature_vector), image_id),
        )

        self.conn.commit()

    def find_similar_drugs_by_features(
        self, target_features: List[float], limit: int = 10
    ) -> List[Dict]:
        """
        根據特徵向量尋找相似藥物

        Args:
            target_features: 目標圖片的特徵向量
            limit: 返回結果數量

        Returns:
            相似藥物列表
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """+-
            SELECT 
                di.id,
                di.image_filename,
                di.image_path,
                d.id as drug_id,
                d.license_number,
                d.chinese_name,
                d.english_name,
                d.shape,
                d.color
            FROM drug_images di
            JOIN drugs d ON di.drug_id = d.id
            WHERE di.feature_vector IS NOT NULL
            LIMIT ?
        """,
            (limit * 5,),
        )  # 先獲取更多結果，再進行相似度計算

        results = [dict(row) for row in cursor.fetchall()]

        # 這裡應該實現向量相似度計算（如餘弦相似度）
        # 暫時返回所有有特徵向量的結果
        return results[:limit]

    # ===== 統計與輔助功能 =====

    def get_statistics(self) -> Dict:
        """獲取資料庫統計資訊"""
        cursor = self.conn.cursor()

        stats = {}

        # 藥物總數
        cursor.execute("SELECT COUNT(*) as count FROM drugs")
        stats["total_drugs"] = cursor.fetchone()[0]

        # 圖片總數
        cursor.execute("SELECT COUNT(*) as count FROM drug_images")
        stats["total_images"] = cursor.fetchone()[0]

        # 有圖片的藥物數
        cursor.execute(
            """
            SELECT COUNT(DISTINCT drug_id) as count FROM drug_images
        """
        )
        stats["drugs_with_images"] = cursor.fetchone()[0]

        # 顏色分布
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
        stats["color_distribution"] = [dict(row) for row in cursor.fetchall()]

        # 形狀分布
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
        stats["shape_distribution"] = [dict(row) for row in cursor.fetchall()]

        return stats


# 使用範例
if __name__ == "__main__":
    # 使用 context manager 自動管理連接
    with DrugDatabase("drug_recognition.db") as db:
        # 範例 1：名稱搜索
        print("=== 搜索「阿斯匹靈」===")
        results = db.search_by_name("阿斯匹靈")
        for drug in results:
            print(
                f"{drug['license_number']}: {drug['chinese_name']} ({drug['image_count']} 張圖片)"
            )

        print("\n=== 搜索白色圓形藥物 ===")
        results = db.search_by_features(shape="圓形", color="白")
        for drug in results[:5]:
            print(
                f"{drug['license_number']}: {drug['chinese_name']} - {drug['shape']}, {drug['color']}"
            )

        print("\n=== 資料庫統計 ===")
        stats = db.get_statistics()
        print(f"藥物總數: {stats['total_drugs']}")
        print(f"圖片總數: {stats['total_images']}")
        print(f"有圖片的藥物: {stats['drugs_with_images']}")
