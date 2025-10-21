# ngrok 設定教學 - 讓您的藥物辨識系統在任何地方都能使用

## 📖 什麼是 ngrok？

**ngrok** 是一個安全的隧道服務，可以將您本地電腦的服務（Flask 伺服器）暴露到公開網路上，讓世界各地的人都能訪問。

### 優點
- ✅ **超級簡單**：一行指令就能啟動
- ✅ **無需路由器設定**：不用搞 Port Forwarding
- ✅ **HTTPS 加密**：自動提供安全連線
- ✅ **穩定網址**：提供固定的公開網址
- ✅ **跨平台**：可以從手機、平板、任何裝置訪問

### 缺點
- ⚠️ 免費版網址會在每次重啟時改變
- ⚠️ 免費版有流量限制（但個人使用足夠）
- ⚠️ 需要網路連線

---

## 🚀 快速開始（5 分鐘搞定）

### Step 1: 註冊 ngrok 帳號

1. 前往 [https://ngrok.com/](https://ngrok.com/)
2. 點擊 **Sign up** 註冊（可使用 Google/GitHub 快速註冊）
3. 註冊完成後會自動導向控制台

### Step 2: 下載 ngrok

#### 方法 A：官網下載（推薦）

1. 前往 [https://ngrok.com/download](https://ngrok.com/download)
2. 選擇 **Windows (64-bit)**
3. 下載 `ngrok-v3-stable-windows-amd64.zip`
4. 解壓縮到任意資料夾（例如：`C:\ngrok\`）

#### 方法 B：使用 Chocolatey

如果您有安裝 Chocolatey 套件管理器：

```powershell
choco install ngrok
```

#### 方法 C：使用 winget

Windows 11 可以使用：

```powershell
winget install ngrok
```

### Step 3: 設定環境變數（可選但建議）

如果您使用方法 A 下載，建議將 ngrok 加入 PATH：

1. 按 `Win + R`，輸入 `sysdm.cpl`，按 Enter
2. 點擊「進階」→「環境變數」
3. 在「系統變數」中找到 `Path`，點擊「編輯」
4. 點擊「新增」，輸入 ngrok.exe 所在路徑（例如：`C:\ngrok\`）
5. 確定並關閉所有視窗

### Step 4: 取得並設定 Authtoken

1. 登入 ngrok 控制台：[https://dashboard.ngrok.com/](https://dashboard.ngrok.com/)
2. 在左側選單點擊 **Your Authtoken**
3. 複製您的 authtoken（格式：`2abc...xyz`）
4. 在 PowerShell 執行：

```powershell
ngrok config add-authtoken <貼上您的token>
```

例如：
```powershell
ngrok config add-authtoken 2abcDEF123xyz456ABC789
```

### Step 5: 啟動伺服器

使用我們提供的一鍵啟動腳本：

```powershell
cd "d:\大學\專題\MUS_Project"
.\start_with_ngrok.ps1
```

或手動啟動（開兩個 PowerShell 視窗）：

**視窗 1：啟動 Flask**
```powershell
cd "d:\大學\專題\MUS_Project"
python app.py
```

**視窗 2：啟動 ngrok**
```powershell
ngrok http 3000
```

### Step 6: 取得公開網址

在 ngrok 視窗中，找到 **Forwarding** 行：

```
Forwarding    https://1234-5678-90ab-cdef.ngrok-free.app -> http://localhost:3000
```

複製這個 `https://...` 網址，就可以在任何地方訪問了！

---

## 📱 測試訪問

### 從手機測試

1. 確保 Flask 和 ngrok 都在運行中
2. 在手機瀏覽器開啟 ngrok 提供的網址
3. 上傳藥物照片進行辨識

### 從其他電腦測試

1. 開啟瀏覽器
2. 輸入 ngrok 網址
3. 開始使用藥物辨識系統

### ngrok 免費版提示頁面

第一次訪問時，ngrok 會顯示一個提示頁面：

```
ngrok - Welcome
You are about to visit https://1234-5678-90ab-cdef.ngrok-free.app
which is served through ngrok.io

Click "Visit Site" to continue
```

點擊 **Visit Site** 即可繼續訪問您的網站。

---

## 🔧 進階設定

### 1. 固定網址（需付費方案）

免費版每次重啟 ngrok 時網址會改變。如果需要固定網址：

1. 升級到付費方案（$8/月起）
2. 在控制台建立 Reserved Domain
3. 啟動時使用：

```powershell
ngrok http --domain=your-domain.ngrok-free.app 3000
```

### 2. 自訂網域（需付費方案）

可以使用自己的網域（例如：api.yourdomain.com）：

1. 在 ngrok 控制台新增 Custom Domain
2. 在您的網域 DNS 設定 CNAME 記錄
3. 啟動時使用：

```powershell
ngrok http --domain=api.yourdomain.com 3000
```

### 3. 基本認證（保護您的服務）

如果想要加密碼保護：

```powershell
ngrok http 3000 --basic-auth="username:password"
```

訪問時會要求輸入帳號密碼。

### 4. 查看請求記錄

ngrok 提供網頁介面查看所有請求：

1. 開啟瀏覽器
2. 前往 `http://127.0.0.1:4040`
3. 可以查看所有 HTTP 請求和回應

### 5. 設定檔案（進階用法）

在 `~/.ngrok2/ngrok.yml` 可以設定更多選項：

```yaml
version: "2"
authtoken: <your_authtoken>
tunnels:
  drug-recognition:
    proto: http
    addr: 3000
    # 可選：固定網址（需付費）
    # domain: your-domain.ngrok-free.app
    # 可選：基本認證
    # auth: "username:password"
```

啟動特定隧道：
```powershell
ngrok start drug-recognition
```

---

## 🔒 安全性考量

### 1. 不要公開分享網址

ngrok 網址可以被任何知道網址的人訪問，因此：

- ❌ 不要在公開論壇發布
- ❌ 不要提交到 GitHub
- ✅ 只分享給信任的人
- ✅ 使用完畢後關閉 ngrok

### 2. 加上認證保護

建議加上密碼保護：

```powershell
ngrok http 3000 --basic-auth="admin:your-secure-password"
```

### 3. 監控訪問記錄

定期檢查 ngrok 控制台的訪問記錄：
- 前往 [https://dashboard.ngrok.com/](https://dashboard.ngrok.com/)
- 查看 **Traffic** 和 **Events**

### 4. 在 Flask 加上 Rate Limiting

修改 `app.py` 加上請求限制（防止濫用）：

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "20 per hour"]
)

@app.route('/api/recognize', methods=['POST'])
@limiter.limit("10 per minute")
def recognize_drug():
    # ... 原有程式碼
```

安裝依賴：
```powershell
pip install Flask-Limiter
```

---

## 📊 ngrok 方案比較

| 功能 | 免費版 | 付費版 ($8/月) |
|------|--------|----------------|
| 隧道數量 | 1 個 | 3+ 個 |
| 網址固定 | ❌ 每次重啟會變 | ✅ 可保留網址 |
| 自訂網域 | ❌ | ✅ |
| 流量限制 | 有限制 | 更高 |
| 請求數 | 40 請求/分鐘 | 無限制 |
| 連線數 | 20 連線 | 無限制 |
| IP 白名單 | ❌ | ✅ |
| TLS 憑證 | ✅ 自動 | ✅ 自動 |

**個人專題使用免費版就足夠！**

---

## 🛠️ 常見問題排解

### 問題 1：`ngrok: command not found`

**原因**：ngrok 未加入 PATH 或未安裝

**解決方法**：
1. 確認 ngrok.exe 位置
2. 使用完整路徑執行：
   ```powershell
   C:\ngrok\ngrok.exe http 3000
   ```
3. 或將路徑加入 PATH 環境變數

### 問題 2：`ERR_NGROK_108: You must sign up to use ngrok`

**原因**：未設定 authtoken

**解決方法**：
```powershell
ngrok config add-authtoken <your_token>
```

### 問題 3：網址無法訪問

**檢查清單**：
1. Flask 伺服器有在運行嗎？（檢查 Flask 視窗）
2. ngrok 有正常啟動嗎？（檢查 ngrok 視窗）
3. 網址複製正確嗎？（https:// 開頭）
4. 網路連線正常嗎？

### 問題 4：網址一直改變

**原因**：免費版每次重啟網址會變

**解決方法**：
- 保持 ngrok 運行不要關閉
- 或升級到付費方案取得固定網址
- 或使用 Dynamic DNS 服務

### 問題 5：速度很慢

**可能原因**：
- 免費版流量限制
- 網路延遲（資料要經過 ngrok 伺服器）

**解決方法**：
- 升級付費方案
- 或使用 Port Forwarding（需路由器設定）
- 或部署到雲端服務（Render、Heroku）

### 問題 6：出現 `ERR_NGROK_3200`

**原因**：免費版限制（例如：超過流量或連線數）

**解決方法**：
- 等待一段時間後再試
- 減少請求頻率
- 升級付費方案

### 問題 7：CORS 錯誤

**原因**：前端和後端網域不同

**解決方法**：
確認 `app.py` 已設定 CORS（已設定完成）：
```python
from flask_cors import CORS
CORS(app)
```

---

## 💡 使用技巧

### 1. 建立桌面捷徑

建立一個 `.bat` 檔案方便啟動：

**start_ngrok.bat**
```batch
@echo off
cd /d "d:\大學\專題\MUS_Project"
start powershell -NoExit -Command "python app.py"
timeout /t 3
start powershell -NoExit -Command "ngrok http 3000"
```

### 2. 自動複製網址到剪貼簿

修改啟動腳本，自動取得並複製網址：

```powershell
# 啟動 ngrok 並取得網址
$ngrokProcess = Start-Process ngrok -ArgumentList "http 3000" -PassThru
Start-Sleep -Seconds 3

# 呼叫 ngrok API 取得網址
$tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels"
$publicUrl = $tunnels.tunnels[0].public_url

# 複製到剪貼簿
$publicUrl | Set-Clipboard
Write-Host "公開網址已複製到剪貼簿：$publicUrl" -ForegroundColor Green
```

### 3. 使用 QR Code 分享

安裝 qrcode 套件：
```powershell
pip install qrcode[pil]
```

建立 QR Code 產生腳本：
```python
import qrcode
import requests

# 取得 ngrok 網址
tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
url = tunnels['tunnels'][0]['public_url']

# 產生 QR Code
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(url)
qr.make(fit=True)
qr.print_ascii()  # 在終端機顯示

# 儲存圖片
img = qr.make_image(fill_color="black", back_color="white")
img.save("ngrok_qrcode.png")
print(f"QR Code 已儲存，掃描即可訪問：{url}")
```

### 4. 自動通知

啟動成功後自動發送通知（例如透過 LINE Notify）：

```python
import requests

def send_line_notify(message, token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    requests.post(url, headers=headers, data=data)

# 使用
send_line_notify(f"藥物辨識系統已啟動\n網址：{ngrok_url}", "your_line_token")
```

---

## 📈 效能優化

### 1. 使用最近的 ngrok 節點

在 ngrok.yml 設定檔指定區域：

```yaml
region: ap  # 亞太區域（最快）
# 其他選項: us, eu, au, sa, jp, in
```

啟動時指定：
```powershell
ngrok http 3000 --region=ap
```

### 2. 壓縮回應

在 Flask 啟用壓縮：

```python
from flask_compress import Compress
Compress(app)
```

安裝：
```powershell
pip install Flask-Compress
```

### 3. 快取靜態資源

在 Flask 設定快取標頭：

```python
@app.after_request
def add_header(response):
    if request.path.startswith('/static'):
        response.cache_control.max_age = 31536000  # 1 年
    return response
```

---

## 🔄 與其他方案比較

| 方案 | 優點 | 缺點 | 適用情境 |
|------|------|------|----------|
| **ngrok** | 最簡單、HTTPS、穩定 | 網址會變、有流量限制 | 臨時分享、Demo、開發測試 |
| **Port Forwarding** | 免費、速度快 | 需路由器權限、安全風險 | 長期使用、內網分享 |
| **Cloudflare Tunnel** | 免費、無限流量、固定網址 | 設定較複雜 | 長期使用、正式環境 |
| **雲端部署** | 穩定、專業 | 可能有費用、部署較複雜 | 正式產品、公開服務 |

**推薦：先用 ngrok 測試，滿意後再考慮其他方案。**

---

## 📚 相關資源

### 官方文件
- [ngrok 官方網站](https://ngrok.com/)
- [ngrok 文件](https://ngrok.com/docs)
- [ngrok GitHub](https://github.com/inconshreveable/ngrok)

### 替代方案
- [Cloudflare Tunnel](https://www.cloudflare.com/products/tunnel/) - 免費、無限流量
- [LocalTunnel](https://localtunnel.github.io/www/) - 開源替代品
- [Pagekite](https://pagekite.net/) - 另一個隧道服務

### 其他教學
- [LOCAL_SERVER_SETUP.md](./LOCAL_SERVER_SETUP.md) - 本地伺服器完整指南
- [MODELS_INTEGRATION.md](./MODELS_INTEGRATION.md) - 模型整合文件
- [README.md](./README.md) - 專案說明

---

## 🎯 總結

使用 ngrok 的步驟：

1. ✅ 註冊並下載 ngrok
2. ✅ 設定 authtoken
3. ✅ 執行 `start_with_ngrok.ps1`
4. ✅ 複製公開網址
5. ✅ 在任何地方訪問！

**就是這麼簡單！** 🎉

---

**最後更新**：2025年10月22日  
**維護者**：MUS_Project Team

有任何問題歡迎在 [GitHub Issues](https://github.com/sunmin-oss/MUS_Project/issues) 提出！
