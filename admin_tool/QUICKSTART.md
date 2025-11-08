# C# WinForms 藥物管理系統 - 快速指南

## 🚀 快速啟動

```powershell
cd "d:\大學\專題\MUS_Project\admin_tool"
.\start_admin.ps1
```

或直接執行:
```powershell
dotnet run
```

## 📋 主要功能

### 1. 資料瀏覽
- DataGridView 顯示所有藥物資料
- 自動調整欄位寬度
- 單選整列模式

### 2. 搜尋 & 篩選
- **搜尋框**: 輸入關鍵字,搜尋許可證字號、中文品名、英文品名
- **劑型下拉**: 篩選特定形狀(全部劑型/錠劑/膠囊等)
- **顏色下拉**: 篩選特定顏色(全部顏色/白色/紅色等)
- **月份下拉**: 篩選更新月份(01-12)
- **Enter 鍵**: 搜尋框按 Enter 立即搜尋

### 3. CRUD 操作

#### 新增藥物
1. 點選「新增」按鈕
2. 填寫資料(許可證字號、中文品名為必填)
3. 點選「儲存」

#### 編輯藥物
1. 選擇表格中的一筆資料
2. 點選「編輯」按鈕
3. 修改欄位
4. 點選「儲存」

#### 刪除藥物
1. 選擇表格中的一筆資料
2. 點選「刪除」按鈕
3. 確認刪除(會同時刪除關聯圖片記錄)

### 4. 圖片檢視
1. 選擇表格中的一筆資料
2. 點選「查看圖片」按鈕
3. 使用「上一張」/「下一張」瀏覽
4. 圖片自動縮放以符合視窗大小

### 5. 重新整理
點選「重新整理」清除所有篩選條件,重新載入全部資料

## 🔧 技術細節

- **框架**: .NET 6.0 Windows
- **UI**: WinForms
- **資料庫**: SQLite (System.Data.SQLite.Core 1.0.118)
- **資料綁定**: DataTable → DataGridView
- **圖片格式**: 支援 JPG, PNG, GIF, BMP

## 📁 檔案說明

| 檔案 | 用途 |
|------|------|
| `Program.cs` | 程式進入點 |
| `MainForm.cs/Designer.cs` | 主視窗 UI 和邏輯 |
| `DrugEditForm.cs/Designer.cs` | 新增/編輯表單 |
| `ImageViewerForm.cs/Designer.cs` | 圖片檢視器 |
| `DrugDatabase.cs` | SQLite 資料存取層 |
| `DrugManagementSystem.csproj` | 專案設定檔 |
| `start_admin.ps1` | PowerShell 啟動腳本 |

## ⚙️ 設定說明

### 資料庫路徑
預設從專案根目錄(`d:\大學\專題\MUS_Project\`)尋找 `drug_recognition.db`

如需修改路徑,編輯 `MainForm.cs`:
```csharp
string dbPath = Path.GetFullPath(Path.Combine(projectRoot, "drug_recognition.db"));
```

### 圖片資料夾路徑
預設從專案根目錄尋找 `medicine_photos` 資料夾

如需修改路徑,編輯 `MainForm.cs`:
```csharp
photoDirectory = Path.GetFullPath(Path.Combine(projectRoot, "medicine_photos"));
```

## 🐛 疑難排解

### 錯誤: 找不到資料庫檔案
```
找不到資料庫檔案:D:\大學\專題\MUS_Project\drug_recognition.db
```
**解決**: 確認 `drug_recognition.db` 存在於專案根目錄

### 錯誤: SQLite DLL 載入失敗
```
Unable to load DLL 'SQLite.Interop.dll'
```
**解決**:
```powershell
dotnet clean
dotnet restore
dotnet build
```

### 圖片無法顯示
**可能原因**:
- `medicine_photos` 資料夾不存在
- `drug_images` 表中的 `image_filename` 錯誤
- 圖片檔案已被刪除

**檢查方式**:
```powershell
Test-Path "d:\大學\專題\MUS_Project\medicine_photos"
```

## 📝 開發注意事項

### 修改 UI 設計
1. 開啟 Visual Studio
2. 雙擊 `MainForm.cs` 或 `DrugEditForm.cs`
3. 使用設計器拖曳控制項
4. 修改會自動反映到 `.Designer.cs` 檔案

### 新增資料庫欄位
1. 修改 `DrugDatabase.cs` 的 SQL 查詢
2. 更新 `DrugEditForm.cs` 的欄位
3. 在 `DrugEditForm.Designer.cs` 新增對應控制項

### 除錯模式
```powershell
dotnet build --configuration Debug
dotnet run --configuration Debug
```

## 📊 效能建議

- **大量資料**: 目前載入 4775 筆資料約需 0.5-1 秒
- **圖片載入**: 使用 FileStream 避免檔案鎖定
- **記憶體管理**: PictureBox.Image 在切換時自動釋放

## 🎯 未來改進方向

- [ ] 分頁功能(每頁 100 筆)
- [ ] 匯出 CSV/Excel
- [ ] 批次圖片上傳
- [ ] 操作日誌記錄
- [ ] 資料庫備份/還原
- [ ] 進階搜尋(多條件 AND/OR)

## 📞 支援

如有問題請參考 `README.md` 或聯絡開發團隊。
