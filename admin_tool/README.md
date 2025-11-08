# 藥物資料管理系統 (Drug Management System)

這是一個使用 C# WinForms 開發的藥物資料庫管理工具,提供 CRUD 功能、圖片檢視及多條件搜尋。

## 功能特色

- ✅ **完整 CRUD 操作**:新增、編輯、刪除藥物資料
- ✅ **多條件篩選**:依劑型、顏色、月份篩選
- ✅ **關鍵字搜尋**:搜尋許可證字號、中文品名、英文品名
- ✅ **圖片檢視**:顯示藥物圖片,支援多圖片切換
- ✅ **DataGridView 顯示**:表格化呈現所有欄位

## 系統需求

- **.NET 6.0 SDK** 或更高版本
- **Windows 作業系統**
- **drug_recognition.db** 資料庫檔案(位於專案根目錄)
- **medicine_photos** 圖片資料夾(位於專題根目錄)

## 資料庫結構

### drugs 資料表
- `id`: 主鍵
- `license_number`: 許可證字號 (必填)
- `chinese_name`: 中文品名 (必填)
- `english_name`: 英文品名
- `shape`: 形狀
- `special_dosage_form`: 特殊劑型
- `color`: 顏色
- `special_odor`: 特殊氣味
- `mark`: 刻痕
- `size`: 外觀尺寸
- `label_front`: 標註一
- `label_back`: 標註二

### drug_images 資料表
- `id`: 主鍵
- `drug_id`: 外鍵,關聯至 drugs.id
- `image_filename`: 圖片檔名

## 安裝步驟

### 1. 確認 .NET 6 SDK 已安裝

```powershell
dotnet --version
```

如果未安裝,請前往 [Microsoft .NET 下載頁面](https://dotnet.microsoft.com/download/dotnet/6.0) 下載安裝。

### 2. 還原 NuGet 套件

```powershell
cd d:\大學\專題\MUS_Project\admin_tool
dotnet restore
```

### 3. 建置專案

```powershell
dotnet build
```

### 4. 執行程式

```powershell
dotnet run
```

或在 Visual Studio 中開啟 `DrugManagementSystem.csproj` 後按 F5 執行。

## 使用說明

### 搜尋與篩選
1. 在搜尋框輸入關鍵字(許可證字號/中文品名/英文品名)
2. 使用下拉選單選擇劑型、顏色、月份
3. 按下「搜尋」按鈕或按 Enter 鍵
4. 按下「重新整理」清除條件並重新載入所有資料

### 新增藥物
1. 按下「新增」按鈕
2. 填寫必填欄位(許可證字號、中文品名)
3. 填寫其他選填欄位
4. 按下「儲存」

### 編輯藥物
1. 在表格中選擇一筆資料
2. 按下「編輯」按鈕
3. 修改欄位內容
4. 按下「儲存」

### 刪除藥物
1. 在表格中選擇一筆資料
2. 按下「刪除」按鈕
3. 確認刪除對話框

### 查看圖片
1. 在表格中選擇一筆資料
2. 按下「查看圖片」按鈕
3. 使用「上一張」/「下一張」切換圖片

## 專案結構

```
admin_tool/
├── DrugManagementSystem.csproj   # 專案檔
├── Program.cs                     # 程式進入點
├── DrugDatabase.cs                # 資料存取層
├── MainForm.cs                    # 主視窗邏輯
├── MainForm.Designer.cs           # 主視窗 UI 設計
├── DrugEditForm.cs                # 編輯表單邏輯
├── DrugEditForm.Designer.cs       # 編輯表單 UI 設計
├── ImageViewerForm.cs             # 圖片檢視器邏輯
├── ImageViewerForm.Designer.cs    # 圖片檢視器 UI 設計
└── README.md                      # 本說明文件
```

## 疑難排解

### 問題:找不到資料庫檔案

**解決方案**:
1. 確認 `drug_recognition.db` 在專案根目錄 (`d:\大學\專題\MUS_Project\`)
2. 檢查 `MainForm.cs` 中的資料庫路徑設定

### 問題:無法顯示圖片

**解決方案**:
1. 確認 `medicine_photos` 資料夾存在
2. 檢查 `drug_images` 資料表中的 `image_filename` 是否正確
3. 確認圖片檔案實際存在於 `medicine_photos` 資料夾

### 問題:編譯錯誤

**解決方案**:
```powershell
# 清理並重建
dotnet clean
dotnet restore
dotnet build
```

### 問題:SQLite DLL 載入失敗

**解決方案**:
1. 確認 System.Data.SQLite.Core 套件已正確安裝
2. 嘗試重新安裝套件:
```powershell
dotnet remove package System.Data.SQLite.Core
dotnet add package System.Data.SQLite.Core --version 1.0.118
```

## 開發環境

- **IDE**: Visual Studio 2022 / VS Code + C# Extension
- **Framework**: .NET 6.0 Windows
- **Database**: SQLite 3
- **UI**: WinForms

## 作者

MUS_Project Team

## 版本歷程

- **v1.0.0** (2025-01): 初始版本,完整 CRUD + 圖片檢視功能

## 授權

本專案僅供學術用途使用。
