# 藥物辨識系統 - 使用 ngrok 啟動（任何地方都能訪問）

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   藥物辨識系統 - ngrok 公網啟動" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 進入專案目錄
$projectPath = "d:\大學\專題\MUS_Project"
Set-Location $projectPath

# 檢查 Python
Write-Host "🔍 檢查環境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 找不到 Python！" -ForegroundColor Red
    exit 1
}

# 檢查 ngrok
Write-Host ""
Write-Host "🌐 檢查 ngrok..." -ForegroundColor Yellow
try {
    $ngrokVersion = ngrok version 2>&1
    Write-Host "  ✅ ngrok: $ngrokVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 找不到 ngrok！" -ForegroundColor Red
    Write-Host ""
    Write-Host "請按照以下步驟安裝 ngrok：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. 前往 https://ngrok.com/download" -ForegroundColor White
    Write-Host "2. 下載 Windows 版本" -ForegroundColor White
    Write-Host "3. 解壓縮到任意資料夾" -ForegroundColor White
    Write-Host "4. 將 ngrok.exe 所在路徑加入 PATH 環境變數" -ForegroundColor White
    Write-Host ""
    Write-Host "或者使用 Chocolatey 安裝：" -ForegroundColor Cyan
    Write-Host "  choco install ngrok" -ForegroundColor Gray
    Write-Host ""
    Write-Host "安裝後執行：" -ForegroundColor Cyan
    Write-Host "  ngrok config add-authtoken <你的token>" -ForegroundColor Gray
    Write-Host "  （token 從 https://dashboard.ngrok.com/get-started/your-authtoken 取得）" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

# 檢查 ngrok authtoken
Write-Host ""
Write-Host "🔑 檢查 ngrok 認證..." -ForegroundColor Yellow
$ngrokConfig = "$env:USERPROFILE\.ngrok2\ngrok.yml"
if (Test-Path $ngrokConfig) {
    $hasAuthtoken = Select-String -Path $ngrokConfig -Pattern "authtoken:" -Quiet
    if ($hasAuthtoken) {
        Write-Host "  ✅ ngrok authtoken 已設定" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  ngrok authtoken 未設定" -ForegroundColor Yellow
        Write-Host "     請執行：ngrok config add-authtoken <你的token>" -ForegroundColor Gray
        Write-Host "     從這裡取得 token：https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠️  ngrok 設定檔不存在" -ForegroundColor Yellow
    Write-Host "     請執行：ngrok config add-authtoken <你的token>" -ForegroundColor Gray
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 準備啟動伺服器..." -ForegroundColor Green
Write-Host ""
Write-Host "  本地伺服器將在 port 3000 運行" -ForegroundColor White
Write-Host "  ngrok 會建立一個公開網址指向您的伺服器" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Cyan
Write-Host "  • 啟動後會開啟兩個視窗：Flask 伺服器 + ngrok 隧道" -ForegroundColor White
Write-Host "  • ngrok 會顯示公開網址（https://xxxx.ngrok-free.app）" -ForegroundColor White
Write-Host "  • 這個網址可以在任何地方訪問（包括手機、外網）" -ForegroundColor White
Write-Host "  • 按 Ctrl+C 可停止伺服器（需要在兩個視窗都停止）" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# 等待使用者確認
Write-Host "按任意鍵啟動..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "🔧 正在啟動 Flask 伺服器..." -ForegroundColor Yellow

# 啟動 Flask（在新視窗）
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; Write-Host '🚀 Flask 伺服器運行中...' -ForegroundColor Green; Write-Host ''; python app.py"

# 等待 Flask 啟動
Write-Host "  等待 Flask 啟動..." -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🌍 正在啟動 ngrok 隧道..." -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  請查看 ngrok 視窗中的公開網址" -ForegroundColor Cyan
Write-Host "  格式：https://xxxx-xxx-xxx-xxx.ngrok-free.app" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# 啟動 ngrok（在新視窗）
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '🌐 ngrok 隧道運行中...' -ForegroundColor Green; Write-Host ''; Write-Host '複製下方的 Forwarding 網址（https://...）即可在任何地方訪問' -ForegroundColor Yellow; Write-Host ''; ngrok http 3000"

Write-Host ""
Write-Host "✅ 啟動完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📝 使用說明：" -ForegroundColor Cyan
Write-Host "  1. 查看 ngrok 視窗，找到 Forwarding 行" -ForegroundColor White
Write-Host "  2. 複製 https://xxxx.ngrok-free.app 網址" -ForegroundColor White
Write-Host "  3. 在任何裝置的瀏覽器開啟這個網址" -ForegroundColor White
Write-Host "  4. 享受您的藥物辨識系統！" -ForegroundColor White
Write-Host ""
Write-Host "🔒 安全提示：" -ForegroundColor Yellow
Write-Host "  • ngrok 免費版每個網址在關閉後會改變" -ForegroundColor Gray
Write-Host "  • 不要分享網址給不信任的人" -ForegroundColor Gray
Write-Host "  • 可以在 ngrok 控制台查看訪問記錄" -ForegroundColor Gray
Write-Host ""
Write-Host "按任意鍵關閉此訊息視窗..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
