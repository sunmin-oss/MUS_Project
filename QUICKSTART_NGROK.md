# 🚀 快速啟動指南 - 在任何地方使用藥物辨識系統

## 只需 3 步驟！

### 第一步：安裝 ngrok（只需做一次）

1. 前往 https://ngrok.com/ 註冊帳號（可用 Google 登入）
2. 下載 Windows 版：https://ngrok.com/download
3. 解壓縮到任意資料夾（例如：`C:\ngrok\`）

### 第二步：設定 authtoken（只需做一次）

1. 登入 ngrok：https://dashboard.ngrok.com/
2. 複製您的 authtoken
3. 在 PowerShell 執行：

```powershell
C:\ngrok\ngrok.exe config add-authtoken <貼上您的token>
```

### 第三步：啟動系統

執行我們的一鍵啟動腳本：

```powershell
cd "d:\大學\專題\MUS_Project"
.\start_with_ngrok.ps1
```

---

## 📱 開始使用

啟動後，查看 **ngrok 視窗**，找到這一行：

```
Forwarding    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:3000
```

複製 `https://...` 網址，就可以：

- ✅ 在手機瀏覽器開啟
- ✅ 在平板開啟
- ✅ 在任何電腦開啟
- ✅ 分享給朋友使用

**不論在哪裡，只要有網路就能使用！** 🌍

---

## ⚠️ 重要提醒

- 每次重啟網址會改變（免費版限制）
- 不要分享網址給不信任的人
- 使用完畢記得關閉伺服器

---

## 💡 常見問題

### Q: 找不到 ngrok 指令？

把 ngrok.exe 所在路徑加入環境變數，或使用完整路徑：

```powershell
C:\ngrok\ngrok.exe http 3000
```

### Q: 網址無法訪問？

檢查：
1. Flask 伺服器有在運行嗎？
2. ngrok 有正常啟動嗎？
3. 網址複製正確嗎？（要 https:// 開頭）

### Q: 想要固定網址？

免費版每次網址會變，需要付費方案（$8/月）才能固定網址。

---

## 📚 詳細文檔

- [NGROK_SETUP.md](./NGROK_SETUP.md) - ngrok 完整教學
- [LOCAL_SERVER_SETUP.md](./LOCAL_SERVER_SETUP.md) - 其他網路設定方式
- [README.md](./README.md) - 專案說明

---

**就是這麼簡單！開始享受您的藥物辨識系統吧！** 🎉
