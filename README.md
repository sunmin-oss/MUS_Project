# 藥物辨識系統 MUS_Project

[![Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://mus-project.vercel.app/)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://mus-project.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org/)

一個以 Flask + SQLite 提供 API、前端使用單檔 Vue 3（CDN）+ Tailwind 的藥物查詢/辨識原型。

## 🚀 線上連結

- **網站**：<https://mus-project.vercel.app/>
- **網站＿ngrok**:<https://talitha-crushable-carlene.ngrok-free.dev/#>
- **後端 API**：<https://mus-project.onrender.com>
- **健康檢查**：<https://mus-project.onrender.com/health>

---

## 📋 專案介紹

這是一個藥物辨識與查詢系統，整合以下技術：

- 後端：`Flask` 提供搜尋 API 與靜態頁面、圖片服務
- 資料庫：`SQLite`，來源為 `medicine_data.csv`
- 前端：單檔 `index.html`（位於專案根目錄），直接向後端 API 發請求
- **圖片辨識**：基於 OpenCV 的影像特徵比對，識別藥物

### ✨ 主要功能

1. **藥物名稱搜尋**：支援中文拆詞模糊搜尋
2. **藥物外觀搜尋**：依形狀、顏色等特徵搜尋
3. **圖片辨識**：上傳藥物照片，自動識別並返回最相似藥物
4. **藥物詳情**：顯示許可證字號、成分、外觀特徵、圖片等完整資訊
- 前端：單檔 `index.html`（位於專案根目錄），直接向後端 API 發請求

> 本專案已部署至 Vercel（前端）與 Render（後端）。若本機啟動 Flask，預設在 [http://127.0.0.1:3000](http://127.0.0.1:3000)

---

## 📂 專案結構

```
MUS_Project/
├── 📁 核心檔案
│   ├── app.py                    # Flask 主程式入口
│   ├── database_query.py         # 資料庫查詢封裝
│   ├── image_recognition.py      # 圖片辨識模組（特徵比對、LBP）
│   ├── ocr_module.py            # OCR 文字辨識模組
│   └── index.html               # 前端頁面（Vue 3 + Tailwind）
│
├── 📁 資料檔案
│   ├── medicine_data.csv        # 藥物原始資料
│   ├── drug_recognition.db      # SQLite 資料庫（.gitignore）
│   ├── medicine_photos/         # 藥物圖片資料夾（.gitignore）
│   └── uploads/                 # 上傳圖片暫存（.gitignore）
│
├── 📁 scripts/                   # 工具腳本
│   ├── create_database.py       # 建立/初始化資料庫
│   ├── download_medicine_photos.py  # 下載藥物圖片
│   ├── sync_images.py           # 同步圖片資料
│   ├── view_database.py         # 查看資料庫內容
│   ├── setup_ngrok.ps1          # ngrok 設定腳本
│   ├── start_server.ps1         # 啟動伺服器
│   └── start_with_ngrok.ps1     # 一鍵啟動伺服器+ngrok
│
├── 📁 tests/                     # 測試檔案
│   ├── test_lbp_features.py     # LBP 特徵測試
│   └── test_recognition.py      # 辨識功能測試
│
├── 📁 docs/                      # 文檔資料
│   ├── DATABASE_README.md       # 資料庫結構說明
│   ├── DATABASE_README_SQLite.md
│   ├── LBP_FEATURES_README.md   # LBP 紋理特徵說明
│   ├── LOCAL_SERVER_SETUP.md    # 本地伺服器設定
│   ├── MODELS_INTEGRATION.md    # 模型整合文件
│   ├── NGROK_SETUP.md           # ngrok 完整設定
│   ├── QUICKSTART_NGROK.md      # ngrok 快速指南
│   ├── ngrok_安裝步驟.md
│   ├── 技術棧討論-2025-09-20.md
│   ├── 技術棧討論-2025-09-23.md
│   ├── 藥物辨識系統專題對話紀錄.md
│   ├── 想法.txt
│   └── MUS_報告.pdf
│
├── 📁 config/                    # 配置檔案
│   ├── robots.txt               # SEO 爬蟲規則
│   ├── sitemap.xml              # 網站地圖
│   ├── .vercelignore            # Vercel 部署忽略
│   ├── googlef01fd03eb85a4416.html  # Google 驗證
│   ├── ngrok_page.html          # ngrok 測試頁面
│   └── ngrok_recovery_codes.txt # ngrok 備份碼
│
└── 📁 其他
    ├── requirements.txt         # Python 依賴套件
    ├── README.md               # 專案說明文件
    ├── .gitignore              # Git 忽略規則
    └── .gitattributes          # Git 屬性設定
```

---

## ⚙️ 環境需求

- Python 3.10 以上（Windows / PowerShell）
- 套件：Flask, flask-cors, opencv-python, numpy

安裝依賴套件（PowerShell）

```powershell
# 建議使用虛擬環境（可選）
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安裝所有依賴
pip install -r requirements.txt
```

---

## 🗄️ 建立資料庫與圖片（首次執行）

專案預設不將 SQLite 與大量圖片納入版本控制，首次請在專案根目錄建立：

```powershell
# 切換到專案根目錄（注意：Windows 路徑含中文/空白建議用 cd 實際進入）
cd "d:\大學\專題\MUS_Project"

# 1) 建立資料庫（由 CSV 匯入）
python scripts\create_database.py
# 成功後會產生 drug_recognition.db

# 2) （可選）下載藥物圖片到 medicine_photos/
python scripts\download_medicine_photos.py
```

> 若尚未下載圖片，前端會顯示「無圖片」占位，不影響基本搜尋與欄位顯示。

---

## 🚀 啟動方式

### 方法 1：本地網路啟動（同 WiFi 裝置可訪問）

```powershell
# 確保位於專案根目錄
cd "d:\大學\專題\MUS_Project"

# 啟動 Flask（內建服務靜態頁面與圖片）
python app.py
```

啟動後：

- 本機訪問：[http://127.0.0.1:3000](http://127.0.0.1:3000)
- 同 WiFi 裝置訪問：`http://192.168.1.104:3000`（請替換為您的內網 IP）

### 方法 2：使用 ngrok（任何地方都能訪問）🌍 ⭐ 推薦

讓您的系統可以從網路上任何地方訪問（手機、平板、其他網路）：

```powershell
# 一鍵啟動（會同時啟動 Flask 和 ngrok）
.\scripts\start_with_ngrok.ps1
```

詳細設定請看：[📖 ngrok 快速指南](./docs/QUICKSTART_NGROK.md)

### 方法 3：線上部署版本

- 前端（Vercel）：<https://mus-project.vercel.app/>
- 後端 API（Render）：<https://mus-project.onrender.com>

前端功能：

- 首頁可輸入藥物名稱搜尋。已支援「連續字串自動拆詞」：
  - 輸入「福元蘇打錠500毫克」會自動拆成「福元 蘇打錠 500 毫克」提高命中率
- **圖片辨識**：
  - 點擊上傳區域選擇藥物照片
  - 點擊「辨識藥物」進行自動識別
  - 顯示最相似的藥物列表及相似度
- 搜尋結果可點「查看詳情」進入詳情頁
- 詳情頁顯示：許可證字號、中文/英文名、形狀、顏色、特殊劑型、特殊氣味、刻痕、外觀尺寸、圖片（如有）

---

## 🔌 API 速覽

- GET `/api/search/name`
  - Query：`q`（字串，支援模糊）、`limit`（預設 20）
  - 範例：`/api/search/name?q=福元`、`/api/search/name?q=福元 蘇打錠500毫克`
  - 回傳：`{ success, count, data: [ { id, license_number, chinese_name, english_name, shape, color, special_dosage_form, images: [...] } ] }`

- GET `/api/search/features`
  - Query：`q`（形狀）、`color`、`label`、`limit`
  - 範例：`/api/search/features?color=白&shape=圓形`

- GET `/api/drug/<id>`
  - 取得單筆完整資訊（含 images）

- **POST `/api/recognize`** ✨ 新功能
  - 藥物圖片辨識 API
  - 參數（multipart/form-data）：
    - `image`：圖片檔案（必需，支援 png, jpg, jpeg, gif, bmp）
    - `top_k`：返回前 K 個結果（選填，預設 5）
    - `is_prescription`：是否為藥單模式（選填，預設 false）
  - 回傳：`{ success, count, data: [ { ...drug_info, similarity, similarity_percent } ] }`

- GET `/images/<filename>`
  - 提供圖片靜態檔（來源：`medicine_photos/`）

- GET `/`
  - 服務前端頁面 `index.html`

- GET `/health`
  - 健康檢查端點

---

## ❓ 常見問題（FAQ / Troubleshooting）

- 啟動後無法開啟或 API 404：
  - 請確認使用 [http://127.0.0.1:3000](http://127.0.0.1:3000) 開啟（不要用 `file://`）
  - 確保 `app.py` 正在執行且顯示沒有錯誤
- 圖片無法顯示：
  - 確認 `medicine_photos/` 存在對應檔名；未下載圖片則會顯示「無圖片」
- 中文/空白路徑問題（Windows）：
  - 建議使用 `cd` 進入專案後再執行指令，或將路徑以引號包起來
- 連續字串搜尋不準：
  - 前端已自動拆詞；若要後端也支援多關鍵字 AND 模糊比對，可再擴充 `database_query.py` 的 `search_by_name`

---

## 🛠️ 開發補充

- `scripts/view_database.py`：快速檢視資料庫內容
- `docs/DATABASE_README.md` / `docs/DATABASE_README_SQLite.md`：資料庫結構與說明
- `tests/`：測試檔案資料夾
  - `test_lbp_features.py`：測試 LBP 紋理特徵
  - `test_recognition.py`：測試辨識功能
- `.gitignore`：已忽略 SQLite、圖片、快取、暫存等

---

## 📚 相關文檔

- [docs/QUICKSTART_NGROK.md](./docs/QUICKSTART_NGROK.md) - **ngrok 快速啟動指南（3 分鐘上手）**
- [docs/NGROK_SETUP.md](./docs/NGROK_SETUP.md) - ngrok 完整設定教學與進階功能
- [docs/LOCAL_SERVER_SETUP.md](./docs/LOCAL_SERVER_SETUP.md) - 本地伺服器設定指南（多種網路方案）
- [docs/MODELS_INTEGRATION.md](./docs/MODELS_INTEGRATION.md) - 圖片辨識模型整合文件
- [docs/LBP_FEATURES_README.md](./docs/LBP_FEATURES_README.md) - LBP 紋理特徵與刻痕比對說明
- [docs/DATABASE_README.md](./docs/DATABASE_README.md) - 資料庫結構說明

---

## �📌 後續規劃（建議）

- 後端搜尋升級：`search_by_name` 支援多關鍵字 AND 模糊條件（API 端也能單獨達到高命中）
- 新增 `/health` 健康檢查路由，方便監控與自動化
- 建立 `requirements.txt`（目前僅需 Flask），方便一鍵安裝

---

## 📄 授權

此專案為學術/課程專題用途。若要公開或商用，請先確認資料來源授權與圖片版權。
