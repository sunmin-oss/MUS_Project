# 藥物辨識系統 MUS_Project

[![Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel)](https://mus-project.vercel.app/)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://mus-project.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org/)

一個以 Flask + SQLite 提供 API、前端使用單檔 Vue 3（CDN）+ Tailwind 的藥物查詢/辨識原型。

## 🚀 線上連結

- **網站**：<https://mus-project.vercel.app/>
- **後端 API**：<https://mus-project.onrender.com>
- **健康檢查**：<https://mus-project.onrender.com/health>

---

## 📋 專案介紹

這是一個藥物辨識與查詢系統，整合以下技術：

- 後端：`Flask` 提供搜尋 API 與靜態頁面、圖片服務
- 資料庫：`SQLite`，來源為 `medicine_data.csv`
- 前端：單檔 `index.html`（位於專案根目錄），直接向後端 API 發請求

> 本專案已部署至 Vercel（前端）與 Render（後端）。若本機啟動 Flask，預設在 [http://127.0.0.1:3000](http://127.0.0.1:3000)

---

## 📂 目錄結構（重點）

- `app.py`：Flask 入口，提供 API 與靜態檔案服務
- `database_query.py`：資料庫查詢封裝（名稱/外觀特徵/圖片/統計）
- `create_database.py`：建立/初始化 `drug_recognition.db`（由 `medicine_data.csv` 匯入）
- `download_medicine_photos.py`：選用，下載藥物圖片至 `medicine_photos/`
- `index.html`：前端頁面（Vue 3 + Tailwind；同一檔在 Vercel 以靜態網站部署）
- `medicine_data.csv`：藥物原始資料（CSV）
- `medicine_photos/`：藥物圖片（本機檔案夾；已在 .gitignore 排除）
- `drug_recognition.db`：SQLite 資料庫檔（已在 .gitignore 排除）

---

## ⚙️ 環境需求

- Python 3.10 以上（Windows / PowerShell）
- 套件：Flask

安裝 Flask（PowerShell）

```powershell
# 建議使用虛擬環境（可選）
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安裝 Flask
pip install Flask
```

---

## 🗄️ 建立資料庫與圖片（首次執行）

專案預設不將 SQLite 與大量圖片納入版本控制，首次請在專案根目錄建立：

```powershell
# 切換到專案根目錄（注意：Windows 路徑含中文/空白建議用 cd 實際進入）
cd "d:\大學\專題\MUS_Project"

# 1) 建立資料庫（由 CSV 匯入）
python create_database.py
# 成功後會產生 drug_recognition.db

# 2) （可選）下載藥物圖片到 medicine_photos/
python download_medicine_photos.py
```

> 若尚未下載圖片，前端會顯示「無圖片」占位，不影響基本搜尋與欄位顯示。

---

## 🚀 啟動後端與開啟前端

```powershell
# 確保位於專案根目錄
cd "d:\大學\專題\MUS_Project"

# 啟動 Flask（內建服務靜態頁面與圖片）
python app.py
```

啟動後瀏覽器開啟（本機開發）：

- 後端 API（本機）：[http://127.0.0.1:3000](http://127.0.0.1:3000)
- 前端（線上正式站）：<https://mus-project.vercel.app/>
- 前端（本機預覽，直接開啟 `index.html` 亦可；預設 API 指向雲端後端）

前端功能：

- 首頁可輸入藥物名稱搜尋。已支援「連續字串自動拆詞」：
  - 輸入「福元蘇打錠500毫克」會自動拆成「福元 蘇打錠 500 毫克」提高命中率
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

- GET `/images/<filename>`
  - 提供圖片靜態檔（來源：`medicine_photos/`）

- GET `/`
  - 服務前端頁面 `drug-recognition-demo/index.html`

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

- `view_database.py`：快速檢視資料庫內容
- `DATABASE_README.md` / `DATABASE_README_SQLite.md`：資料庫結構與說明
- `.gitignore`：已忽略 SQLite、圖片、快取、暫存等

---

## 📌 後續規劃（建議）

- 後端搜尋升級：`search_by_name` 支援多關鍵字 AND 模糊條件（API 端也能單獨達到高命中）
- 新增 `/health` 健康檢查路由，方便監控與自動化
- 建立 `requirements.txt`（目前僅需 Flask），方便一鍵安裝

---

## 📄 授權

此專案為學術/課程專題用途。若要公開或商用，請先確認資料來源授權與圖片版權。
