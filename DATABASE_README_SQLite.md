# 藥物辨識系統 - 資料庫設計文檔 (SQLite 版本)

## 資料庫架構說明

本系統使用 **SQLite** 作為資料庫，檔案名稱為 `drug_recognition.db`。SQLite 無需安裝額外的資料庫伺服器，適合開發和小型應用部署。

### 資料表結構

#### 1. drugs（藥物基本資料表）
存儲藥物的基本資訊和外觀特徵。

| 欄位名稱 | 資料類型 | 說明 |
|---------|---------|------|
| id | INTEGER | 主鍵（自動遞增）|
| license_number | TEXT | 許可證字號（唯一識別）|
| chinese_name | TEXT | 中文品名 |
| english_name | TEXT | 英文品名 |
| shape | TEXT | 形狀 |
| special_dosage_form | TEXT | 特殊劑型 |
| color | TEXT | 顏色 |
| special_odor | TEXT | 特殊氣味 |
| mark | TEXT | 刻痕 |
| size | TEXT | 外觀尺寸 |
| label_front | TEXT | 標註一 |
| label_back | TEXT | 標註二 |
| created_at | TEXT | 建立時間 (ISO 8601 格式) |
| updated_at | TEXT | 更新時間 (ISO 8601 格式) |

#### 2. drug_images（藥物圖片表）
存儲藥物的圖片資訊，與 drugs 表是一對多關係。

| 欄位名稱 | 資料類型 | 說明 |
|---------|---------|------|
| id | INTEGER | 主鍵（自動遞增）|
| drug_id | INTEGER | 外鍵，關聯到 drugs.id |
| image_filename | TEXT | 圖檔名稱 |
| image_path | TEXT | 圖檔完整路徑 |
| image_order | INTEGER | 圖片順序（第1張、第2張等）|
| feature_vector | TEXT | 圖像特徵向量（JSON 格式，AI 模型提取）|
| created_at | TEXT | 建立時間 (ISO 8601 格式) |

### 索引設計

為了提升查詢效率，建立了以下索引：

- **藥物表索引**：
  - `idx_drugs_license`: 許可證字號索引（用於快速查找）
  - `idx_drugs_chinese_name`: 中文品名索引（用於名稱搜索）
  - `idx_drugs_english_name`: 英文品名索引（用於名稱搜索）
  - `idx_drugs_color`: 顏色索引（用於特徵搜索）
  - `idx_drugs_shape`: 形狀索引（用於特徵搜索）

- **圖片表索引**：
  - `idx_drug_images_drug_id`: 藥物 ID 索引（用於關聯查詢）
  - `idx_drug_images_filename`: 檔案名稱索引

## 安裝與設置

### 1. SQLite 安裝

SQLite 是 Python 的內建模組，無需額外安裝。如果需要命令列工具：

**Windows:**
```powershell
# SQLite3 已內建在 Python 中
# 如果需要命令列工具，可從 https://www.sqlite.org/download.html 下載
```

**Mac:**
```bash
# SQLite 已預裝
sqlite3 --version
```

**Linux:**
```bash
# 通常已預裝，如需安裝：
sudo apt install sqlite3
```

### 2. 建立資料庫與匯入資料

執行以下指令來建立資料庫並匯入 CSV 資料：

```bash
# 在專案目錄下執行
python create_database.py
```

執行後會：
1. 建立 `drug_recognition.db` 檔案
2. 建立 `drugs` 和 `drug_images` 資料表
3. 建立所有索引
4. 從 `medicine_data.csv` 匯入藥物資料
5. 自動關聯 `medicine_photos/` 資料夾中的圖片

### 3. 驗證資料庫

**使用 Python 查詢：**
```bash
python database_query.py
```

**使用 SQLite 命令列：**
```bash
sqlite3 drug_recognition.db

# 查看所有資料表
.tables

# 查看資料表結構
.schema drugs
.schema drug_images

# 統計資料
SELECT COUNT(*) FROM drugs;
SELECT COUNT(*) FROM drug_images;

# 查詢範例
SELECT license_number, chinese_name, color, shape 
FROM drugs 
WHERE chinese_name LIKE '%普拿疼%';

# 離開
.quit
```

## 資料庫操作指南

### 使用 Python 查詢資料庫

本專案提供了 `database_query.py` 工具類別，方便進行資料庫操作。

#### 基本使用範例

```python
from database_query import DrugDatabase

# 使用 context manager 自動管理連接
with DrugDatabase('drug_recognition.db') as db:
    # 1. 名稱搜索
    results = db.search_by_name("普拿疼")
    for drug in results:
        print(f"{drug['chinese_name']} - {drug['license_number']}")
    
    # 2. 特徵搜索
    results = db.search_by_features(shape="圓形", color="白")
    for drug in results:
        print(f"{drug['chinese_name']}: {drug['shape']}, {drug['color']}")
    
    # 3. 獲取完整藥物資訊（含圖片）
    drug = db.get_drug_with_images(drug_id=1)
    print(f"藥物: {drug['chinese_name']}")
    print(f"圖片數量: {len(drug['images'])}")
    
    # 4. 獲取統計資訊
    stats = db.get_statistics()
    print(f"藥物總數: {stats['total_drugs']}")
    print(f"圖片總數: {stats['total_images']}")
```

### 主要查詢方法

#### 1. search_by_name(query, limit=20)
根據藥物名稱進行模糊搜索。

```python
results = db.search_by_name("維他命", limit=10)
```

**返回欄位：**
- id, license_number, chinese_name, english_name
- shape, color, special_dosage_form
- image_count（圖片數量）

#### 2. search_by_features(shape, color, label, limit=20)
根據外觀特徵搜索。

```python
results = db.search_by_features(
    shape="橢圓", 
    color="白", 
    label="A",
    limit=20
)
```

**返回欄位：**
- id, license_number, chinese_name, english_name
- shape, color, mark, label_front, label_back
- image_count

#### 3. get_drug_images(drug_id)
獲取特定藥物的所有圖片。

```python
images = db.get_drug_images(drug_id=1)
for img in images:
    print(img['image_filename'])
    print(img['image_path'])
```

#### 4. get_all_drug_images()
獲取所有藥物圖片（用於 AI 模型訓練）。

```python
all_images = db.get_all_drug_images()
print(f"總共 {len(all_images)} 張圖片")
```

#### 5. get_drug_with_images(drug_id)
獲取藥物完整資訊，包含所有圖片。

```python
drug = db.get_drug_with_images(drug_id=1)
print(drug['chinese_name'])
print(drug['images'])  # 圖片列表
```

#### 6. update_image_features(image_id, feature_vector)
更新圖片的 AI 特徵向量。

```python
features = [0.1, 0.2, 0.3, ...]  # AI 模型提取的特徵
db.update_image_features(image_id=1, feature_vector=features)
```

#### 7. get_statistics()
獲取資料庫統計資訊。

```python
stats = db.get_statistics()
print(stats['total_drugs'])
print(stats['total_images'])
print(stats['color_distribution'])  # 顏色分布
print(stats['shape_distribution'])  # 形狀分布
```

## Flask API 整合範例

以下是如何在 Flask 後端中使用資料庫：

```python
from flask import Flask, jsonify, request
from database_query import DrugDatabase

app = Flask(__name__)

@app.route('/api/search/name', methods=['GET'])
def search_by_name():
    """名稱搜索 API"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    
    with DrugDatabase() as db:
        results = db.search_by_name(query, limit)
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })

@app.route('/api/search/features', methods=['GET'])
def search_by_features():
    """特徵搜索 API"""
    shape = request.args.get('shape')
    color = request.args.get('color')
    label = request.args.get('label')
    limit = int(request.args.get('limit', 20))
    
    with DrugDatabase() as db:
        results = db.search_by_features(shape, color, label, limit)
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })

@app.route('/api/drug/<int:drug_id>', methods=['GET'])
def get_drug_detail(drug_id):
    """獲取藥物詳細資訊"""
    with DrugDatabase() as db:
        drug = db.get_drug_with_images(drug_id)
        if drug:
            return jsonify({
                'success': True,
                'data': drug
            })
        else:
            return jsonify({
                'success': False,
                'error': '藥物不存在'
            }), 404

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """獲取統計資訊"""
    with DrugDatabase() as db:
        stats = db.get_statistics()
        return jsonify({
            'success': True,
            'data': stats
        })

if __name__ == '__main__':
    app.run(debug=True)
```

## 資料庫維護

### 備份資料庫

```bash
# 直接複製資料庫檔案
cp drug_recognition.db drug_recognition_backup.db

# 或使用 SQLite 備份命令
sqlite3 drug_recognition.db ".backup drug_recognition_backup.db"
```

### 還原資料庫

```bash
# 直接複製備份檔案
cp drug_recognition_backup.db drug_recognition.db
```

### 優化資料庫

```bash
sqlite3 drug_recognition.db "VACUUM;"
```

### 匯出資料

**匯出為 SQL：**
```bash
sqlite3 drug_recognition.db .dump > backup.sql
```

**匯出為 CSV：**
```bash
sqlite3 drug_recognition.db <<EOF
.headers on
.mode csv
.output drugs_export.csv
SELECT * FROM drugs;
.quit
EOF
```

## AI 模型整合說明

### 特徵向量存儲

當 AI 模型（如 CNN）提取圖片特徵後，可以存儲到 `drug_images.feature_vector` 欄位：

```python
import json
import numpy as np
from database_query import DrugDatabase

# 假設 AI 模型已提取特徵
feature_vector = model.extract_features(image)  # 返回 numpy array

# 轉換為列表並存儲
with DrugDatabase() as db:
    db.update_image_features(
        image_id=1, 
        feature_vector=feature_vector.tolist()
    )
```

### 圖片相似度比對

```python
import json
import numpy as np
from database_query import DrugDatabase

def cosine_similarity(vec1, vec2):
    """計算餘弦相似度"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def find_similar_drugs(uploaded_image_features, top_k=10):
    """尋找相似藥物"""
    with DrugDatabase() as db:
        # 獲取所有有特徵向量的圖片
        all_images = db.get_all_drug_images()
        
        similarities = []
        for img in all_images:
            if img['feature_vector']:
                db_features = json.loads(img['feature_vector'])
                similarity = cosine_similarity(
                    uploaded_image_features, 
                    db_features
                )
                similarities.append({
                    'drug_id': img['drug_id'],
                    'drug_name': img['chinese_name'],
                    'image_path': img['image_path'],
                    'similarity': float(similarity)
                })
        
        # 排序並返回 top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]

# 使用範例
results = find_similar_drugs(uploaded_features, top_k=5)
for result in results:
    print(f"{result['drug_name']}: {result['similarity']:.2%}")
```

## 資料統計

執行 `create_database.py` 後的統計結果：

```
=== 資料庫統計 ===
藥物總數: 4416
圖片總數: 4775
有圖片的藥物: 4394
無圖片的藥物: 22
```

### 圖片分布範例

```
=== 圖片最多的藥物（前5名）===
衛署成製字第015063號 - 千鶴薄荷棒: 16 張圖片
衛署藥製字第031016號 - "光南" 治嗽糖漿: 6 張圖片
衛署藥製字第045389號 - "中美" 伏您炎口腔消炎噴液劑: 5 張圖片
衛署藥製字第057731號 - "晟德"律莎錠: 5 張圖片
衛署藥輸字第020936號 - 卡維傑特注射劑: 5 張圖片
```

## 常見問題

### Q1: 資料庫檔案在哪裡？
A: 資料庫檔案 `drug_recognition.db` 位於專案根目錄。

### Q2: 如何重新建立資料庫？
A: 刪除 `drug_recognition.db` 檔案後，重新執行 `python create_database.py`。

### Q3: SQLite 支援多少資料量？
A: SQLite 理論上支援最大 281 TB 的資料庫大小，對於本專案（約 2.5 MB）綽綽有餘。

### Q4: 可以改回 PostgreSQL 嗎？
A: 可以。原始的 PostgreSQL 版本文檔在 `DATABASE_README.md`，程式碼邏輯相似，只需修改連接方式和語法。

### Q5: 如何在 Flask 中提供圖片？
A: 使用 Flask 的 `send_from_directory`：

```python
from flask import send_from_directory

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('medicine_photos', filename)
```

## 下一步

1. **建立 Flask API**：參考上面的 API 範例建立完整的後端服務
2. **整合 AI 模型**：實作圖片特徵提取和相似度比對
3. **前端整合**：連接 Vue.js 前端與 Flask API
4. **部署**：使用 Docker 容器化部署

## 技術支援

- SQLite 官方文檔：https://www.sqlite.org/docs.html
- Python sqlite3 模組：https://docs.python.org/3/library/sqlite3.html
- Flask 官方文檔：https://flask.palletsprojects.com/
