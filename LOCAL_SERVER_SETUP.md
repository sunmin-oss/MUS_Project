# 本地伺服器設定指南

讓你的電腦成為藥物辨識伺服器，讓其他使用者可以連接並使用辨識功能。

## 📋 目前狀態

✅ Flask 已設定為 `host="0.0.0.0"`（對外服務）  
✅ Port: 3000  
✅ 你的內網 IP: `192.168.1.104`

## 🎯 方案選擇

### 方案 A：區域網路（同 WiFi）★ 推薦入門
**適用**：同事、同學在同一個 WiFi 網路下連接  
**優勢**：簡單、快速、無需額外設定  
**步驟**：→ [跳到方案 A](#方案-a區域網路同-wifi)

### 方案 B：公開網路（任何人）★★ 推薦使用
**適用**：讓任何人透過網路連接（包含手機 4G/5G）  
**優勢**：不需要路由器設定、安全、HTTPS 支援  
**步驟**：→ [跳到方案 B](#方案-b公開網路使用-ngrok)

### 方案 C：Port Forwarding
**適用**：有固定 IP 或想要完全掌控  
**缺點**：需要路由器管理權限、可能有安全風險  
**步驟**：→ [跳到方案 C](#方案-cport-forwarding選用)

---

## 方案 A：區域網路（同 WiFi）

### 1. 啟動伺服器

```powershell
# 進入專案目錄
cd "d:\大學\專題\MUS_Project"

# 啟動 Flask
python app.py
```

你會看到：
```
 * Running on http://127.0.0.1:3000
 * Running on http://192.168.1.104:3000
```

### 2. 設定 Windows 防火牆

**方法一：使用指令（推薦）**

以**系統管理員**身分執行 PowerShell：

```powershell
# 新增防火牆規則允許 port 3000
New-NetFirewallRule -DisplayName "藥物辨識系統 Port 3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

**方法二：圖形界面**

1. 開啟「控制台」→「系統及安全性」→「Windows Defender 防火牆」
2. 點擊「進階設定」
3. 左側選「輸入規則」→ 右側點「新增規則」
4. 選擇「連接埠」→ 下一步
5. 選擇「TCP」，特定本機連接埠：`3000`
6. 選擇「允許連線」
7. 套用到「網域」、「私人」、「公用」
8. 名稱：`藥物辨識系統 Port 3000`

### 3. 連線測試

**同一台電腦測試：**
- 開啟瀏覽器：http://127.0.0.1:3000

**同 WiFi 的其他裝置：**
- 開啟瀏覽器：http://192.168.1.104:3000
- 手機、平板、其他電腦都可以

### 4. 分享連結

告訴使用者連接：
```
http://192.168.1.104:3000
```

⚠️ **注意**：每次重新連接 WiFi，你的 IP 可能會改變！重新執行 `ipconfig` 確認。

---

## 方案 B：公開網路（使用 ngrok）

### 為什麼選 ngrok？
- ✅ 免費（有流量限制）
- ✅ 提供 HTTPS 安全連線
- ✅ 不需要路由器設定
- ✅ 可以讓任何人（包含手機網路）連接
- ✅ 穩定的網域名稱

### 1. 安裝 ngrok

**下載並安裝：**
1. 訪問：https://ngrok.com/download
2. 下載 Windows 版本
3. 解壓縮到任意位置（例如 `C:\ngrok\`）

**或使用 Chocolatey：**
```powershell
choco install ngrok
```

### 2. 註冊並認證

1. 註冊免費帳號：https://dashboard.ngrok.com/signup
2. 獲取 authtoken（登入後在 Dashboard）
3. 執行認證：

```powershell
ngrok authtoken <你的_authtoken>
```

### 3. 啟動服務

**終端機 1 - 啟動 Flask：**
```powershell
cd "d:\大學\專題\MUS_Project"
python app.py
```

**終端機 2 - 啟動 ngrok：**
```powershell
ngrok http 3000
```

你會看到類似：
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:3000
```

### 4. 分享連結

**公開網址**（任何人都可以訪問）：
```
https://abc123.ngrok-free.app
```

📱 可以用手機 4G/5G 測試！

### 5. ngrok 進階設定

**自訂網域（付費功能）：**
```powershell
ngrok http 3000 --domain=your-domain.ngrok-free.app
```

**查看訪問日誌：**
- 訪問：http://127.0.0.1:4040
- 可以看到所有請求的詳細資訊

**保持穩定連線：**
- 免費版會在 2 小時後斷線
- 付費版有更長的連線時間和固定網域

---

## 方案 C：Port Forwarding（選用）

⚠️ **警告**：此方法會將你的電腦直接暴露在網路上，需要額外的安全措施！

### 1. 獲取公網 IP

```powershell
# 使用 PowerShell
(Invoke-WebRequest -Uri "https://api.ipify.org").Content
```

或訪問：https://whatismyipaddress.com/

### 2. 設定路由器 Port Forwarding

1. 登入路由器管理界面（通常是 192.168.1.1 或 192.168.0.1）
2. 找到「Port Forwarding」或「虛擬伺服器」設定
3. 新增規則：
   - **外部 Port**：3000（或其他，如 8080）
   - **內部 IP**：192.168.1.104
   - **內部 Port**：3000
   - **協定**：TCP

### 3. 測試連線

**從外網測試：**
```
http://<你的公網IP>:3000
```

### 4. 安全建議

❌ **不推薦長期使用此方法**，因為：
- 電腦直接暴露在網路上
- 容易受到攻擊
- 公網 IP 可能會改變（除非有固定 IP）

**如果必須使用，請：**
1. 使用強密碼保護路由器
2. 定期更新系統
3. 考慮加上 Basic Authentication
4. 使用 HTTPS（需要 SSL 憑證）

---

## 🔒 安全建議

### 1. 加上密碼保護（可選）

在 `app.py` 加上簡單的認證：

```python
from functools import wraps
from flask import request

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.password != "你的密碼":
            return jsonify({"error": "需要認證"}), 401
        return f(*args, **kwargs)
    return decorated

# 套用到路由
@app.route("/api/recognize", methods=["POST"])
@require_auth
def recognize_drug():
    # ... 原有程式碼
```

### 2. 速率限制

安裝並使用 Flask-Limiter：
```powershell
pip install Flask-Limiter
```

### 3. 定期檢查日誌

監控異常的訪問模式。

---

## 📊 效能考量

### 你的電腦需要：
- **記憶體**：至少 4GB（推薦 8GB）
- **CPU**：中等（辨識時會使用較多資源）
- **網路**：穩定的網路連線

### 同時使用者數量：
- **影像特徵模型**：可同時服務 5-10 人
- **OCR 模型**：較耗資源，建議 2-5 人

### 優化建議：
1. 關閉不必要的程式
2. 確保電腦不會進入睡眠模式
3. 使用有線網路（比 WiFi 穩定）

---

## 🐛 故障排除

### 問題 1：無法連接（同 WiFi）

**檢查防火牆：**
```powershell
# 列出防火牆規則
Get-NetFirewallRule -DisplayName "*3000*"
```

**檢查 Flask 是否正在運行：**
```powershell
netstat -an | findstr :3000
```

應該看到：
```
TCP    0.0.0.0:3000           0.0.0.0:0              LISTENING
```

### 問題 2：IP 位址改變

每次重新連接 WiFi 後，執行：
```powershell
ipconfig | findstr /i "IPv4"
```

### 問題 3：ngrok 連線緩慢

- 免費版有流量限制
- 考慮升級或使用 Cloudflare Tunnel

### 問題 4：電腦進入睡眠

**防止睡眠：**
1. 設定 → 系統 → 電源與睡眠
2. 將「電腦進入睡眠狀態」設為「永不」（使用伺服器期間）

---

## 🚀 快速啟動腳本

建立 `start_server.ps1`：

```powershell
# 進入專案目錄
cd "d:\大學\專題\MUS_Project"

# 顯示 IP
Write-Host "=== 你的伺服器資訊 ===" -ForegroundColor Green
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"})[0].IPAddress
Write-Host "內網連結: http://$ip:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "提示：同 WiFi 的使用者可以訪問上面的網址" -ForegroundColor Cyan
Write-Host ""

# 啟動 Flask
Write-Host "正在啟動伺服器..." -ForegroundColor Green
python app.py
```

**使用方式：**
```powershell
# 右鍵執行或
powershell -ExecutionPolicy Bypass -File start_server.ps1
```

---

## 📱 手機連接測試

### iOS / Android

1. 連接到同一個 WiFi（方案 A）
2. 開啟瀏覽器（Safari / Chrome）
3. 輸入：`http://192.168.1.104:3000`
4. 測試上傳照片和辨識功能

### 使用 ngrok（方案 B）

- 可以用手機的 4G/5G 網路測試
- 開啟瀏覽器訪問 ngrok 給的網址

---

## 📚 推薦使用情境

| 情境 | 推薦方案 | 原因 |
|------|----------|------|
| 課堂展示 | A（同 WiFi） | 簡單、快速 |
| 給朋友試用 | B（ngrok） | 不受網路限制 |
| 專題發表 | B（ngrok） | 專業、穩定 |
| 長期運行 | 雲端部署（Render） | 不占用電腦資源 |

---

## ✅ 檢查清單

在開始服務前，確認：

- [ ] Flask 正在運行（`python app.py`）
- [ ] 防火牆規則已新增（port 3000）
- [ ] 知道內網 IP（`ipconfig`）
- [ ] 同 WiFi 裝置可以連接
- [ ] （可選）ngrok 已設定並運行
- [ ] 電腦不會自動睡眠
- [ ] 網路連線穩定

---

## 💡 下一步

1. **測試基本連線**：先用方案 A 在同 WiFi 測試
2. **公開測試**：使用方案 B（ngrok）讓更多人測試
3. **收集反饋**：記錄使用者的問題和建議
4. **優化效能**：根據使用情況調整

---

需要幫助？
- 查看 Flask 終端機的錯誤訊息
- 檢查防火牆設定
- 確認 IP 位址正確
- 測試網路連線

祝你的藥物辨識系統成功運行！🎉
