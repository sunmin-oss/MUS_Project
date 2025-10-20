# 藥物辨識系統 - 資料庫設計文檔

## 資料庫架構說明

### 資料表結構

#### 1. drugs（藥物基本資料表）
存儲藥物的基本資訊和外觀特徵。

| 欄位名稱 | 資料類型 | 說明 |
|---------|---------|------|
| id | SERIAL | 主鍵（自動遞增）|
| license_number | VARCHAR(50) | 許可證字號（唯一識別）|
| chinese_name | VARCHAR(200) | 中文品名 |
| english_name | VARCHAR(200) | 英文品名 |
| shape | VARCHAR(50) | 形狀 |
| special_dosage_form | VARCHAR(100) | 特殊劑型 |
| color | VARCHAR(100) | 顏色 |
| special_odor | VARCHAR(100) | 特殊氣味 |
| mark | VARCHAR(100) | 刻痕 |
| size | VARCHAR(100) | 外觀尺寸 |
| label_front | VARCHAR(200) | 標註一 |
| label_back | VARCHAR(200) | 標註二 |
| created_at | TIMESTAMP | 建立時間 |
| updated_at | TIMESTAMP | 更新時間 |

#### 2. drug_images（藥物圖片表）
存儲藥物的圖片資訊，與 drugs 表是一對多關係。

| 欄位名稱 | 資料類型 | 說明 |
|---------|---------|------|
| id | SERIAL | 主鍵（自動遞增）|
| drug_id | INTEGER | 外鍵，關聯到 drugs.id |
| image_filename | VARCHAR(100) | 圖檔名稱 |
| image_path | VARCHAR(255) | 圖檔完整路徑 |
| image_order | INTEGER | 圖片順序（第1張、第2張等）|
| feature_vector | JSONB | 圖像特徵向量（AI 模型提取）|
| created_at | TIMESTAMP | 建立時間 |

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
  - `idx_drug_images_feature`: 特徵向量 GIN 索引（用於向量搜索）

## 安裝與設置

### 1. 安裝 PostgreSQL

**Windows:**
```powershell
# 下載並安裝 PostgreSQL
# https://www.postgresql.org/download/windows/
```

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. 建立資料庫

```sql
-- 使用 psql 或 pgAdmin 執行
CREATE DATABASE drug_recognition;
```

### 3. 安裝 Python 套件

```bash
pip install psycopg2-binary
# 或者
pip install psycopg2
```

### 4. 設定資料庫連線

修改 `create_database.py` 和 `database_query.py` 中的資料庫設定：

```python
DB_CONFIG = {
    'dbname': 'drug_recognition',
    'user': 'postgres',
    'password': 'your_password',  # 修改為您的密碼
    'host': 'localhost',
    'port': '5432'
}
```

### 5. 執行資料匯入

```bash
python create_database.py
```

## 使用方式

### 基本查詢範例

#### 1. 按名稱搜索藥物

```python
from database_query import DrugDatabase

DB_CONFIG = {
    'dbname': 'drug_recognition',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}

with DrugDatabase(DB_CONFIG) as db:
    # 搜索包含「阿斯匹靈」的藥物
    results = db.search_by_name("阿斯匹靈")
    
    for drug in results:
        print(f"{drug['chinese_name']} - {drug['license_number']}")
        print(f"  顏色: {drug['color']}, 形狀: {drug['shape']}")
        print(f"  圖片數量: {drug['image_count']}")
```

#### 2. 按外觀特徵搜索

```python
with DrugDatabase(DB_CONFIG) as db:
    # 搜索白色圓形藥物
    results = db.search_by_features(shape="圓形", color="白")
    
    for drug in results:
        print(f"{drug['chinese_name']}")
        print(f"  形狀: {drug['shape']}, 顏色: {drug['color']}")
        print(f"  標註: {drug['label_front']} / {drug['label_back']}")
```

#### 3. 獲取藥物完整資訊（含圖片）

```python
with DrugDatabase(DB_CONFIG) as db:
    # 獲取 ID 為 1 的藥物完整資訊
    drug = db.get_drug_with_images(1)
    
    if drug:
        print(f"藥物名稱: {drug['chinese_name']}")
        print(f"許可證字號: {drug['license_number']}")
        print(f"\n圖片列表:")
        for img in drug['images']:
            print(f"  - {img['image_filename']} (順序: {img['image_order']})")
            print(f"    路徑: {img['image_path']}")
```

#### 4. 獲取所有藥物圖片（用於 AI 模型）

```python
with DrugDatabase(DB_CONFIG) as db:
    # 獲取所有圖片（用於訓練或批量比對）
    all_images = db.get_all_drug_images()
    
    print(f"總共有 {len(all_images)} 張圖片")
    
    # 處理每張圖片
    for img in all_images:
        image_path = img['image_path']
        drug_name = img['chinese_name']
        # 這裡可以載入圖片並進行處理
        # image = cv2.imread(image_path)
        # features = extract_features(image)
        # db.update_image_features(img['id'], features)
```

## AI 模型整合

### 圖像識別流程

1. **使用者上傳圖片**
2. **提取圖片特徵向量**（使用 CNN 或 Vision API）
3. **在資料庫中比對**
4. **返回最相似的藥物**

### 特徵向量存儲

```python
# 範例：儲存圖片特徵向量
with DrugDatabase(DB_CONFIG) as db:
    # 假設已經從 AI 模型提取了特徵
    feature_vector = [0.123, 0.456, 0.789, ...]  # 128 或 256 維向量
    
    # 更新資料庫
    db.update_image_features(image_id=1, feature_vector=feature_vector)
```

### 相似度搜索

```python
# 範例：尋找相似藥物
with DrugDatabase(DB_CONFIG) as db:
    # 上傳圖片的特徵向量
    uploaded_image_features = extract_features(uploaded_image)
    
    # 搜索相似藥物
    similar_drugs = db.find_similar_drugs_by_features(
        target_features=uploaded_image_features,
        limit=10
    )
    
    for drug in similar_drugs:
        print(f"{drug['chinese_name']} - 相似度: {drug.get('similarity', 'N/A')}")
```

## Flask API 整合範例

```python
from flask import Flask, request, jsonify
from database_query import DrugDatabase

app = Flask(__name__)

DB_CONFIG = {
    'dbname': 'drug_recognition',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}

@app.route('/api/drugs/search', methods=['GET'])
def search_drugs():
    query = request.args.get('q', '')
    
    with DrugDatabase(DB_CONFIG) as db:
        results = db.search_by_name(query, limit=20)
        return jsonify({
            'success': True,
            'results': results
        })

@app.route('/api/drugs/<int:drug_id>', methods=['GET'])
def get_drug_detail(drug_id):
    with DrugDatabase(DB_CONFIG) as db:
        drug = db.get_drug_with_images(drug_id)
        
        if drug:
            return jsonify({
                'success': True,
                'drug': drug
            })
        else:
            return jsonify({
                'success': False,
                'error': '藥物不存在'
            }), 404

if __name__ == '__main__':
    app.run(debug=True)
```

## 效能優化建議

1. **使用連接池**：在生產環境中使用 `psycopg2.pool` 來管理資料庫連接
2. **批次處理**：大量資料操作時使用批次插入/更新
3. **向量搜索優化**：考慮使用 pgvector 擴展來實現高效的向量相似度搜索
4. **快取機制**：對於常用查詢結果使用 Redis 進行快取

## 故障排除

### 常見問題

1. **無法連接資料庫**
   - 檢查 PostgreSQL 服務是否啟動
   - 確認資料庫設定（用戶名、密碼、主機、端口）是否正確

2. **中文顯示亂碼**
   - 確保資料庫編碼為 UTF-8
   - CSV 檔案使用 UTF-8-BOM 編碼

3. **圖片路徑錯誤**
   - 確認 `medicine_photos` 資料夾存在
   - 檢查圖片檔案名稱是否與許可證字號一致

## 下一步開發

- [ ] 實現向量相似度搜索（使用 pgvector）
- [ ] 添加全文搜索功能優化
- [ ] 實現快取機制
- [ ] 添加 API 認證與授權
- [ ] 實現圖片特徵自動提取流程
