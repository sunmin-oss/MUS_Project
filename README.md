# 🏥 智慧藥物辨識系統 (MUS_Project)

[![Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://mus-project.vercel.app/)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://mus-project.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![C#](https://img.shields.io/badge/C%23-.NET_6-512BD4?style=for-the-badge&logo=csharp&logoColor=white)](https://dotnet.microsoft.com/)

> 一個整合影像辨識、文字識別(OCR)、資料庫管理的全方位藥物查詢與辨識系統，提供 Web 介面與桌面管理工具。

---

## 🚀 線上連結

- **前端網站 (Vercel)**: https://mus-project.vercel.app/
- **前端網站 (ngrok)**: https://talitha-crushable-carlene.ngrok-free.dev/
- **後端 API (Render)**: https://mus-project.onrender.com
- **健康檢查**: https://mus-project.onrender.com/health

---

## 📋 專案簡介

智慧藥物辨識系統是一個完整的藥物管理與辨識解決方案，結合了現代 Web 技術與桌面應用程式，為使用者提供多種藥物查詢與辨識方式。

### 🎯 核心功能

#### 🌐 Web 系統 (使用者介面)

1. **藥物名稱搜尋**
   - 支援中文/英文模糊搜尋
   - 自動拆詞技術，提高搜尋準確度
   - 即時顯示搜尋結果與藥物圖片

2. **藥物外觀搜尋**
   - 依形狀、顏色等特徵篩選
   - 支援多條件組合查詢
   - 視覺化呈現藥物特徵

3. **智慧圖片辨識** ⭐
   - **自動模式**: 系統自動判斷使用何種辨識方法
   - **影像特徵比對**: 基於 OpenCV 的 LBP 紋理特徵比對
   - **OCR 文字辨識**: 辨識藥袋、藥盒上的文字
   - **藥單模式**: 一次辨識多種藥物
   - 支援形狀/顏色預篩選，提升辨識速度
   - 即時進度顯示與取消功能

4. **藥物詳細資訊**
   - 基本資訊: 許可證字號、中/英文名稱、外觀特徵
   - **臨床資訊** (NEW!):
     - 適應症
     - 用法用量
     - 副作用
     - 禁忌症
     - 注意事項
     - 主要成分
     - 藥品分類
     - 製造商
     - 儲存條件
     - 有效期限資訊
   - 多張藥物圖片展示

#### 🖥️ 管理系統 (C# WinForms)

1. **藥物資料管理**
   - 新增、編輯、刪除藥物資料
   - 支援 21 個欄位的完整資料輸入
   - 三分頁介面設計: 基本資訊、臨床資訊、其他資訊

2. **圖片管理**
   - 上傳與管理藥物圖片
   - 圖片預覽功能
   - 批次圖片處理

3. **資料庫操作**
   - 即時資料同步
   - 模糊搜尋功能
   - DataGridView 資料展示

---

## 🛠️ 技術架構

### 後端技術

- **框架**: Flask 2.x (Python)
- **資料庫**: SQLite 3
- **影像處理**: OpenCV, NumPy, Pillow
- **OCR**: PaddleOCR (可選)
- **API**: RESTful API 設計
- **跨域**: Flask-CORS

### 前端技術

- **框架**: Vue.js 3 (CDN)
- **樣式**: Tailwind CSS
- **圖示**: Font Awesome 6
- **響應式**: Mobile-First 設計

### 管理工具

- **語言**: C# .NET 6
- **UI框架**: Windows Forms
- **資料庫連接**: System.Data.SQLite.Core 1.0.118
- **架構模式**: MVC 模式

### 部署平台

- **前端**: Vercel (靜態網站)
- **後端**: Render (容器部署)
- **本地網路**: ngrok (公網穿透)

---

## 🔄 系統運作流程

### 1️⃣ 藥物搜尋流程

```
使用者輸入關鍵字
    ↓
前端自動拆詞處理
    ↓
發送 API 請求到 Flask
    ↓
DrugDatabase 查詢 SQLite
    ↓
返回藥物列表 + 圖片資訊
    ↓
Vue.js 渲染結果到頁面
```

### 2️⃣ 圖片辨識流程

```
使用者上傳藥物照片
    ↓
選擇辨識模式 (自動/特徵/OCR/藥單)
    ↓
Flask 接收圖片並儲存
    ↓
┌─────────────┬─────────────┬─────────────┐
│  特徵比對   │  OCR 辨識   │  藥單模式   │
├─────────────┼─────────────┼─────────────┤
│ 提取 LBP    │ PaddleOCR   │ OCR + 多筆  │
│ 特徵向量    │ 提取文字    │ 藥物匹配    │
│ 計算相似度  │ 模糊搜尋    │ 批次處理    │
└─────────────┴─────────────┴─────────────┘
    ↓
返回相似度排序結果
    ↓
前端顯示辨識結果
    ↓
使用者查看詳細資訊
```

### 3️⃣ 資料管理流程

```
管理員啟動 C# 管理系統
    ↓
連接 drug_recognition.db
    ↓
┌──────────┬──────────┬──────────┐
│  新增    │  編輯    │  刪除    │
└──────────┴──────────┴──────────┘
    ↓
填寫 21 個欄位資料
    ↓
DrugDatabase.cs 執行 SQL
    ↓
資料寫入 SQLite
    ↓
Web API 即時讀取更新
```

### 4️⃣ 資料流向圖

```
┌─────────────────────────────────────────────────┐
│                  資料來源                        │
│  medicine_data.csv (4775+ 筆藥物原始資料)        │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
        create_database.py
                 │
                 ↓
┌────────────────────────────────────────────────┐
│         drug_recognition.db (SQLite)           │
│  ┌──────────────┬───────────────────────────┐ │
│  │ drugs 表     │ drug_images 表            │ │
│  │ (24 欄位)    │ (圖片資訊 + LBP 特徵)     │ │
│  └──────────────┴───────────────────────────┘ │
└──────┬─────────────────────────────────┬──────┘
       │                                  │
       ↓                                  ↓
┌──────────────┐                  ┌──────────────┐
│  Flask API   │                  │  C# 管理系統  │
│  (讀取)      │                  │  (CRUD)      │
└──────┬───────┘                  └──────────────┘
       │
       ↓
┌──────────────┐
│ Vue.js 前端  │
│ (顯示)       │
└──────────────┘
```

---

## 📂 專案結構

```
MUS_Project/
│
├── 🌐 Web 系統
│   ├── app.py                      # Flask 主程式 (API + 靜態服務)
│   ├── index.html                  # 前端頁面 (Vue 3 + Tailwind)
│   ├── database_query.py           # 資料庫查詢封裝層
│   ├── image_recognition.py        # 影像辨識模組 (LBP 特徵比對)
│   └── ocr_module.py              # OCR 文字辨識模組 (PaddleOCR)
│
├── 🖥️ 管理系統 (admin_tool/)
│   ├── Program.cs                  # C# 程式進入點
│   ├── MainForm.cs                 # 主視窗 (藥物列表與搜尋)
│   ├── DrugEditForm.cs            # 編輯視窗 (3 分頁表單)
│   ├── DrugDatabase.cs            # 資料庫操作類別 (CRUD)
│   ├── ImageViewerForm.cs         # 圖片檢視器
│   ├── start_admin.ps1            # 啟動腳本
│   ├── QUICKSTART.md              # 快速入門指南
│   ├── CLINICAL_FIELDS.md         # 臨床欄位說明文件
│   └── DrugManagementSystem.csproj # 專案設定檔
│
├── 📊 資料檔案
│   ├── medicine_data.csv          # 原始藥物資料 (4775+ 筆)
│   ├── drug_recognition.db        # SQLite 資料庫 (.gitignore)
│   ├── medicine_photos/           # 藥物圖片資料夾 (.gitignore)
│   └── uploads/                   # 上傳圖片暫存 (.gitignore)
│
├── 🔧 腳本工具 (scripts/)
│   ├── create_database.py         # 建立/初始化資料庫
│   ├── add_clinical_fields.py     # 新增臨床欄位 (資料庫遷移)
│   ├── download_medicine_photos.py # 下載藥物圖片
│   ├── sync_images.py             # 同步圖片到資料庫
│   ├── view_database.py           # 查看資料庫內容
│   ├── setup_ngrok.ps1            # ngrok 設定腳本
│   ├── start_server.ps1           # 啟動 Flask 伺服器
│   └── start_with_ngrok.ps1       # 一鍵啟動 (Flask + ngrok)
│
├── 🧪 測試檔案 (tests/)
│   ├── test_lbp_features.py       # LBP 特徵提取測試
│   └── test_recognition.py        # 辨識功能測試
│
├── 📚 文檔資料 (docs/)
│   ├── DATABASE_README.md         # 資料庫結構詳細說明
│   ├── DATABASE_README_SQLite.md  # SQLite 特定文件
│   ├── LBP_FEATURES_README.md     # LBP 紋理特徵原理
│   ├── LOCAL_SERVER_SETUP.md      # 本地伺服器設定
│   ├── MODELS_INTEGRATION.md      # 辨識模型整合文件
│   ├── NGROK_SETUP.md             # ngrok 完整設定教學
│   ├── QUICKSTART_NGROK.md        # ngrok 3 分鐘快速指南
│   ├── PROJECT_ORGANIZATION.md    # 專案組織架構
│   ├── 技術棧討論-2025-09-20.md  # 技術選型討論
│   ├── 技術棧討論-2025-09-23.md  # 技術選型討論
│   └── 藥物辨識系統專題對話紀錄.md # 開發紀錄
│
├── ⚙️ 配置檔案
│   ├── requirements.txt           # Python 依賴套件
│   ├── .gitignore                 # Git 忽略規則
│   ├── .vercelignore              # Vercel 部署忽略
│   ├── config/
│   │   ├── robots.txt             # SEO 爬蟲規則
│   │   ├── sitemap.xml            # 網站地圖
│   │   └── googlef01fd03eb85a4416.html # Google 驗證
│   └── 專題.sln                   # Visual Studio 解決方案檔
│
└── 📖 README.md                   # 本文件
```

---

## 🗄️ 資料庫結構

### drugs 資料表 (24 欄位)

#### 基本資訊 (12 欄位)

- `id`: 主鍵
- `license_number`: 許可證字號 (唯一索引)
- `chinese_name`: 中文名稱
- `english_name`: 英文名稱
- `shape`: 形狀
- `color`: 顏色
- `mark`: 刻痕
- `size`: 外觀尺寸
- `special_dosage_form`: 特殊劑型
- `special_odor`: 特殊氣味
- `label_front`: 標註一 (正面)
- `label_back`: 標註二 (背面)

#### 臨床資訊 (10 欄位) - NEW! 🎉

- `indications`: 適應症
- `dosage`: 用法用量
- `side_effects`: 副作用
- `contraindications`: 禁忌症
- `precautions`: 注意事項
- `ingredient`: 主要成分
- `category`: 藥品分類
- `manufacturer`: 製造商
- `storage_conditions`: 儲存條件
- `expiry_info`: 有效期限資訊

#### 時間戳記 (2 欄位)

- `created_at`: 建立時間
- `updated_at`: 更新時間

### drug_images 資料表

- `id`: 主鍵
- `drug_id`: 外鍵 (關聯到 drugs.id)
- `image_filename`: 圖片檔名
- `image_path`: 圖片路徑
- `image_order`: 圖片順序
- `feature_vector`: LBP 特徵向量 (JSON)

---

## ⚙️ 環境需求

### 系統需求

- **作業系統**: Windows 10/11 (PowerShell 5.1+)
- **Python**: 3.10 或以上
- **.NET**: .NET 6 SDK (管理系統需要)

### Python 套件依賴

```txt
Flask>=2.0.0
flask-cors>=3.0.0
opencv-python>=4.5.0
numpy>=1.21.0
Pillow>=9.0.0
paddleocr>=2.6.0 (選用，OCR 功能需要)
paddlepaddle>=2.4.0 (選用，OCR 功能需要)
```

### C# 專案依賴

```xml
System.Data.SQLite.Core (1.0.118)
```

---

## 🚀 快速開始

### 步驟 1: 安裝 Python 依賴套件

```powershell
# 切換到專案目錄
cd "d:\大學\專題\MUS_Project"

# (可選) 建立虛擬環境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安裝依賴套件
pip install -r requirements.txt
```

### 步驟 2: 建立資料庫

```powershell
# 從 CSV 建立 SQLite 資料庫
python scripts\create_database.py

# (可選) 下載藥物圖片
python scripts\download_medicine_photos.py
```

### 步驟 3: 啟動系統

#### 選項 A: 啟動 Web 系統 (本地網路)

```powershell
# 啟動 Flask 伺服器
python app.py
```

訪問: <http://127.0.0.1:3000>

#### 選項 B: 啟動 Web 系統 (公網訪問) ⭐ 推薦

```powershell
# 步驟 1: 啟動 Flask 伺服器
python app.py

# 步驟 2: 開啟新的 PowerShell 視窗，啟動 ngrok
ngrok http 3000
```

獲得 ngrok 提供的公網網址，可從任何裝置訪問!

**一鍵啟動 (可選)**:
```powershell
# 如果腳本可用，也可使用一鍵啟動
.\scripts\start_with_ngrok.ps1
```

#### 選項 C: 啟動管理系統

```powershell
# 切換到管理工具目錄
cd admin_tool

# 編譯並執行
dotnet run

# 或直接執行已編譯版本
dotnet run --no-build
```

---

## 📡 API 文件

### 🔍 搜尋 API

#### 1. 藥物名稱搜尋

```http
GET /api/search/name?q={關鍵字}&limit={數量}
```

**參數**:

- `q`: 搜尋關鍵字 (中文/英文)
- `limit`: 返回結果數量 (預設: 20)

**範例**:

```text
/api/search/name?q=癌必莎爾
/api/search/name?q=普拿疼&limit=10
```

**回應**:

```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": 1234,
      "license_number": "衛部藥製字第XXXXX號",
      "chinese_name": "癌必莎爾膜衣錠",
      "english_name": "...",
      "shape": "圓形",
      "color": "白色",
      "images": [
        {
          "image_filename": "xxx.jpg",
          "image_order": 1
        }
      ]
    }
  ]
}
```

#### 2. 藥物特徵搜尋

```http
GET /api/search/features?shape={形狀}&color={顏色}&label={標註}&limit={數量}
```

**參數**:

- `shape`: 形狀 (圓形/橢圓形/方形/...)
- `color`: 顏色 (白/黃/紅/藍/...)
- `label`: 標註文字
- `limit`: 返回結果數量 (預設: 20)

**範例**:

```text
/api/search/features?shape=圓形&color=白
```

#### 3. 藥物詳情

```http
GET /api/drug/{藥物ID}
```

**範例**:

```text
/api/drug/1234
```

**回應**: 包含所有 24 個欄位及圖片資訊

### 🖼️ 辨識 API

#### 藥物圖片辨識

```http
POST /api/recognize
Content-Type: multipart/form-data
```

**參數**:

- `image`: 圖片檔案 (必需)
- `model`: 辨識模式 (選填)
  - `auto`: 自動判斷 (預設)
  - `feature`: 影像特徵比對
  - `ocr`: OCR 文字辨識
  - `prescription`: 藥單模式
- `top_k`: 返回前 K 個結果 (預設: 5)
- `shape`: 形狀篩選 (選填)
- `color`: 顏色篩選 (選填)
- `request_id`: 請求 ID (用於進度追蹤)

**回應**:

```json
{
  "success": true,
  "method": "特徵比對",
  "count": 5,
  "data": [
    {
      "id": 1234,
      "chinese_name": "...",
      "similarity": 0.92,
      "similarity_percent": "92%",
      ...
    }
  ]
}
```

#### 辨識進度查詢

```http
GET /api/progress/{request_id}
```

#### 取消辨識

```http
POST /api/cancel
Content-Type: application/json

{
  "request_id": "xxx"
}
```

### 🖼️ 圖片服務

```http
GET /images/{檔名}
```

**範例**:

```text
/images/衛部藥製字第061466號.jpg
```

### 🏥 健康檢查

```http
GET /health
```

---

## 💡 使用說明

### Web 系統使用

1. **搜尋藥物**
   - 在首頁輸入藥物名稱或關鍵字
   - 系統會自動拆詞提高搜尋準確度
   - 點擊搜尋結果查看詳細資訊

2. **圖片辨識**
   - 選擇辨識模式 (建議使用「自動判斷」)
   - (可選) 選擇形狀/顏色篩選條件
   - 點擊上傳區域選擇藥物照片
   - 點擊「辨識藥物」開始辨識
   - 查看相似度排序結果

3. **查看詳情**
   - 點擊「查看詳情」按鈕
   - 瀏覽基本資訊與臨床資訊
   - 查看藥物圖片

### 管理系統使用

1. **查看藥物列表**
   - 啟動後自動載入所有藥物
   - 使用搜尋框快速查找

2. **新增藥物**
   - 點擊「新增」按鈕
   - 填寫三個分頁的資料:
     - 基本資訊: 許可證字號、名稱、外觀等
     - 臨床資訊: 適應症、用法、副作用等
     - 其他資訊: 成分、分類、製造商等
   - 點擊「儲存」

3. **編輯藥物**
   - 選擇藥物記錄
   - 點擊「編輯」按鈕
   - 修改資料後儲存

4. **刪除藥物**
   - 選擇藥物記錄
   - 點擊「刪除」按鈕
   - 確認刪除

---

## 🔬 辨識技術說明

### 影像特徵比對

使用 **LBP (Local Binary Pattern)** 紋理特徵:

1. 將圖片轉換為灰階
2. 提取 LBP 紋理特徵向量
3. 計算與資料庫中所有藥物圖片的相似度
4. 返回相似度最高的 Top-K 結果

**優點**: 對光照變化具有魯棒性  
**適用**: 單顆藥物清晰照片

### OCR 文字辨識

使用 **PaddleOCR** 進行文字識別:

1. 偵測圖片中的文字區域
2. 識別文字內容
3. 與資料庫中藥物名稱進行模糊匹配
4. 返回匹配結果

**優點**: 可識別藥袋、藥盒上的文字  
**適用**: 包含文字的藥物包裝

### 自動模式

系統自動判斷圖片類型:

- 檢測到大量文字 → 使用 OCR
- 檢測到單一物體 → 使用特徵比對
- 預設 → 特徵比對

---

## 🛠️ 開發工具

### 資料庫管理

```powershell
# 查看資料庫內容
python scripts\view_database.py

# 新增臨床欄位 (已執行過)
python scripts\add_clinical_fields.py
```

### 圖片管理

```powershell
# 同步圖片到資料庫
python scripts\sync_images.py

# 下載藥物圖片
python scripts\download_medicine_photos.py
```

### 測試

```powershell
# 測試 LBP 特徵提取
python tests\test_lbp_features.py

# 測試辨識功能
python tests\test_recognition.py
```

---

## ❓ 常見問題 FAQ

### Q1: 啟動後無法訪問網頁?

**A**: 請確認:

- 使用 `http://127.0.0.1:3000` 訪問 (不要用 `file://`)
- Flask 正在執行且沒有錯誤訊息
- 防火牆未阻擋 3000 端口

### Q2: 圖片無法顯示?

**A**:

- 確認 `medicine_photos/` 資料夾存在
- 執行 `python scripts\download_medicine_photos.py` 下載圖片
- 未下載圖片時會顯示「無圖片」占位符，不影響功能

### Q3: 辨識速度很慢?

**A**:

- 特徵比對需要計算所有藥物的相似度 (4775+ 筆)
- 使用形狀/顏色篩選可大幅提升速度
- 第一次辨識會預載入部分特徵，後續會較快

### Q4: OCR 辨識失敗?

**A**:

- 確認已安裝 PaddleOCR: `pip install paddleocr paddlepaddle`
- 圖片需包含清晰的文字
- 建議使用「自動模式」讓系統判斷

### Q5: 管理系統無法啟動?

**A**:

- 確認已安裝 .NET 6 SDK
- 執行 `dotnet build` 重新編譯
- 檢查 `drug_recognition.db` 是否存在

### Q6: 新增的臨床資料沒有顯示?

**A**:

- 確認已重啟 Flask 伺服器
- 清除瀏覽器快取
- 檢查資料庫是否包含該筆資料

### Q7: 中文路徑問題?

**A**:

- Windows 建議使用 `cd` 實際進入專案目錄
- 或將路徑用雙引號包起來
- 範例: `cd "d:\大學\專題\MUS_Project"`

---

## 📚 相關文件

### 完整文件

- [📖 資料庫結構說明](./docs/DATABASE_README.md)
- [📖 SQLite 資料庫文件](./docs/DATABASE_README_SQLite.md)
- [📖 LBP 紋理特徵原理](./docs/LBP_FEATURES_README.md)
- [📖 辨識模型整合文件](./docs/MODELS_INTEGRATION.md)
- [📖 專案組織架構](./docs/PROJECT_ORGANIZATION.md)

### 快速指南

- [🚀 ngrok 3分鐘快速指南](./docs/QUICKSTART_NGROK.md)
- [🚀 管理系統快速入門](./admin_tool/QUICKSTART.md)
- [🚀 臨床欄位說明](./admin_tool/CLINICAL_FIELDS.md)

### 進階設定

- [⚙️ ngrok 完整設定教學](./docs/NGROK_SETUP.md)
- [⚙️ 本地伺服器設定](./docs/LOCAL_SERVER_SETUP.md)

### 開發紀錄

- [📝 技術棧討論 (2025-09-20)](./docs/技術棧討論-2025-09-20.md)
- [📝 技術棧討論 (2025-09-23)](./docs/技術棧討論-2025-09-23.md)
- [📝 專題對話紀錄](./docs/藥物辨識系統專題對話紀錄.md)

---

## 🚧 未來規劃

### 短期目標

- [ ] 增加更多藥物臨床資訊
- [ ] 優化辨識速度 (特徵向量快取)
- [ ] 新增使用者收藏功能
- [ ] 改進 OCR 準確度

### 中期目標

- [ ] 開發手機 App (React Native)
- [ ] 新增藥物交互作用查詢
- [ ] 批次匯入臨床資料功能
- [ ] 使用者回饋系統

### 長期目標

- [ ] 整合深度學習模型 (CNN)
- [ ] 多語言支援 (英文/日文)
- [ ] 雲端部署優化
- [ ] API 使用權限管理

---

## 👥 貢獻指南

歡迎提交 Issue 或 Pull Request!

### 開發流程

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 程式碼風格

- Python: 遵循 PEP 8
- C#: 遵循 Microsoft C# Coding Conventions
- JavaScript: 使用 ESLint 建議設定

---

## 📄 授權聲明

本專案為學術/課程專題用途。

### 資料來源

- 藥物資料: 衛生福利部食品藥物管理署開放資料
- 圖片來源: 公開資料

### 注意事項

- 本系統僅供參考，不可作為醫療診斷依據
- 使用藥物前請諮詢專業醫療人員
- 若要商用，請先確認資料授權與圖片版權

---

## 📞 聯絡資訊

- **專案負責人**: MUS_Project Team
- **GitHub**: [sunmin-oss/MUS_Project](https://github.com/sunmin-oss/MUS_Project)
- **問題回報**: [GitHub Issues](https://github.com/sunmin-oss/MUS_Project/issues)

---

## 🙏 致謝

感謝以下開源專案與資源:

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Vue.js](https://vuejs.org/) - 前端框架
- [OpenCV](https://opencv.org/) - 影像處理
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR 引擎
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架
- [SQLite](https://www.sqlite.org/) - 資料庫
- [衛生福利部食品藥物管理署](https://www.fda.gov.tw/) - 藥物資料

---

<div align="center">

**智慧藥物辨識系統** | Made with ❤️ by MUS_Project Team

⭐ 如果這個專案對您有幫助，請給我們一個 Star!

</div>
