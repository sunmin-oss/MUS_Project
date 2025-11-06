"""
資料庫查詢工具 - 提供給 AI 模型使用的查詢功能 (SQLite 版本)
"""

import sqlite3
import os
from typing import List, Dict, Optional


class DrugDatabase:
    """藥物資料庫查詢類別"""

    def __init__(self, db_file: str = "drug_recognition.db"):
        self.db_file = db_file
        self.conn = None

    def connect(self):
        """建立資料庫連接"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # 讓結果可以像字典一樣訪問

    def close(self):
        """關閉資料庫連接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ===== 名稱搜索功能 =====

    def search_by_name(self, query: str, limit: int = 20) -> List[Dict]:
        """
        根據藥物名稱搜索（支援模糊搜索）

        Args:
            query: 搜索關鍵字（中文或英文）
            limit: 返回結果數量限制

        Returns:
            符合條件的藥物列表
        """
        cursor = self.conn.cursor()

        cursor.execute(
            """
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
                d.chinese_name LIKE ? OR 
                d.english_name LIKE ?
            GROUP BY d.id
            ORDER BY 
                CASE 
                    WHEN d.chinese_name LIKE ? THEN 1
                    WHEN d.english_name LIKE ? THEN 2
                    ELSE 3
                END,
                d.chinese_name
            LIMIT ?
        """,
            (f"%{query}%", f"%{query}%", f"{query}%", f"{query}%", limit),
        )

        return [dict(row) for row in cursor.fetchall()]

    def search_by_features(
        self, shape: str = None, color: str = None, label: str = None, limit: int = 20
    ) -> List[Dict]:
        """
        根據藥物外觀特徵搜索

        Args:
            shape: 形狀
            color: 顏色
            label: 標註（標註一或標註二）
            limit: 返回結果數量限制

        Returns:
            符合條件的藥物列表
        """
        cursor = self.conn.cursor()

        conditions = []
        params = []

        if shape:
            conditions.append("d.shape LIKE ?")
            params.append(f"%{shape}%")

        if color:
            conditions.append("d.color LIKE ?")
            params.append(f"%{color}%")

        if label:
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
        """取得單一藥物基本資訊（不含圖片）。"""

        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT *
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
