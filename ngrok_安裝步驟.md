# ngrok 安裝與設定步驟（手把手教學）

## 📥 Step 1: 下載 ngrok

1. **前往 ngrok 下載頁面**
   - 網址：https://ngrok.com/download
   - 或直接下載：https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip

2. **選擇 Windows 64-bit 版本**
   - 點擊下載按鈕
   - 檔案名稱：`ngrok-v3-stable-windows-amd64.zip`

3. **解壓縮檔案**
   - 在下載資料夾找到 `ngrok-v3-stable-windows-amd64.zip`
   - 右鍵 → 解壓縮全部
   - 建議解壓到：`C:\ngrok\`
   - 解壓後會得到 `ngrok.exe`

---

## 🔧 Step 2: 設定 ngrok 路徑

### 方法 A：加入 PATH 環境變數（推薦）

1. **開啟系統環境變數**
   - 按 `Win + R`
   - 輸入 `sysdm.cpl`
   - 按 Enter

2. **編輯 PATH**
   - 點擊「進階」標籤
   - 點擊「環境變數」
   - 在「系統變數」中找到 `Path`
   - 點擊「編輯」

3. **新增 ngrok 路徑**
   - 點擊「新增」
   - 輸入 ngrok.exe 所在資料夾路徑（例如：`C:\ngrok\`）
   - 確定並關閉所有視窗

4. **重新開啟 PowerShell**
   - 關閉所有 PowerShell 視窗
   - 重新開啟 PowerShell
   - 測試：`ngrok version`

### 方法 B：使用完整路徑（簡單但每次都要輸入）

不加入 PATH，每次使用完整路徑執行：

```powershell
C:\ngrok\ngrok.exe version
```

---

## 🔑 Step 3: 取得 authtoken

1. **登入 ngrok**
   - 前往：https://dashboard.ngrok.com/
   - 使用您註冊的帳號登入

2. **複製 authtoken**
   - 左側選單點擊「Your Authtoken」
   - 點擊「Copy」複製您的 token
   - 格式類似：`2abc...xyz`（很長一串）

---

## ⚙️ Step 4: 設定 authtoken

### 如果已加入 PATH：

```powershell
ngrok config add-authtoken <貼上您的token>
```

### 如果使用完整路徑：

```powershell
C:\ngrok\ngrok.exe config add-authtoken <貼上您的token>
```

**範例**（請替換為您的實際 token）：
```powershell
ngrok config add-authtoken 2abcDEF123xyz456ABC789GHI012JKL345MNO678PQR901STU234
```

執行成功會顯示：
```
Authtoken saved to configuration file: C:\Users\您的使用者名稱\.ngrok2\ngrok.yml
```

---

## ✅ Step 5: 驗證安裝

測試 ngrok 是否正常運作：

### 如果已加入 PATH：
```powershell
ngrok version
```

### 如果使用完整路徑：
```powershell
C:\ngrok\ngrok.exe version
```

應該會顯示類似：
```
ngrok version 3.x.x
```

---

## 🚀 Step 6: 啟動藥物辨識系統

### 方法 1：使用自動化腳本（推薦）

如果 ngrok 已加入 PATH：

```powershell
cd "d:\大學\專題\MUS_Project"
.\start_with_ngrok.ps1
```

### 方法 2：手動啟動

**開啟第一個 PowerShell 視窗（Flask）：**
```powershell
cd "d:\大學\專題\MUS_Project"
python app.py
```

**開啟第二個 PowerShell 視窗（ngrok）：**

如果已加入 PATH：
```powershell
ngrok http 3000
```

如果使用完整路徑：
```powershell
C:\ngrok\ngrok.exe http 3000
```

---

## 📱 Step 7: 取得公開網址

啟動 ngrok 後，在視窗中找到這一行：

```
Forwarding    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:3000
```

複製 `https://...` 開頭的網址，就可以在：
- ✅ 手機瀏覽器
- ✅ 平板
- ✅ 任何電腦
- ✅ 任何網路環境

開啟並使用您的藥物辨識系統！

---

## 🔧 常見問題

### Q1: 執行 ngrok 時出現「無法辨識 'ngrok'」

**原因**：ngrok 未加入 PATH

**解決方法**：
1. 使用完整路徑：`C:\ngrok\ngrok.exe http 3000`
2. 或按照 Step 2 方法 A 加入 PATH

### Q2: 顯示「ERR_NGROK_108」錯誤

**原因**：未設定 authtoken

**解決方法**：
```powershell
ngrok config add-authtoken <您的token>
```

### Q3: 不知道 ngrok.exe 在哪裡

**解決方法**：
在檔案總管搜尋 `ngrok.exe`，或重新下載並解壓到 `C:\ngrok\`

### Q4: authtoken 在哪裡找？

**解決方法**：
1. 前往 https://dashboard.ngrok.com/
2. 左側選單點擊「Your Authtoken」
3. 複製顯示的 token

### Q5: start_with_ngrok.ps1 無法執行

**原因**：腳本假設 ngrok 已在 PATH 中

**解決方法**：
手動啟動（開兩個 PowerShell 視窗，分別執行 Flask 和 ngrok）

---

## 📝 快速複習

1. ✅ 下載 ngrok：https://ngrok.com/download
2. ✅ 解壓縮到 `C:\ngrok\`
3. ✅ 加入 PATH 或使用完整路徑
4. ✅ 取得 authtoken：https://dashboard.ngrok.com/
5. ✅ 設定 authtoken：`ngrok config add-authtoken <token>`
6. ✅ 啟動系統：`.\start_with_ngrok.ps1`
7. ✅ 複製公開網址開始使用！

---

**有任何問題隨時詢問！** 🎉
