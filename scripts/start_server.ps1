# 藥物辨識系統伺服器啟動腳本

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   藥物辨識系統 - 本地伺服器啟動" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 進入專案目錄
$projectPath = "d:\大學\專題\MUS_Project"
Set-Location $projectPath

# 顯示伺服器資訊
Write-Host "🖥️  伺服器資訊：" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 獲取內網 IP
$localIPs = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"}
if ($localIPs) {
    $mainIP = $localIPs[0].IPAddress
    Write-Host "  本機 IP: " -NoNewline
    Write-Host "http://127.0.0.1:3000" -ForegroundColor White
    Write-Host "  內網 IP: " -NoNewline
    Write-Host "http://${mainIP}:3000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  📱 同 WiFi 的裝置可以訪問：" -ForegroundColor Green
    Write-Host "     http://${mainIP}:3000" -ForegroundColor White -BackgroundColor DarkGreen
} else {
    Write-Host "  ⚠️  無法取得內網 IP" -ForegroundColor Red
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# 檢查 Python 是否安裝
Write-Host "🔍 檢查環境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 找不到 Python！請先安裝 Python 3.10 以上" -ForegroundColor Red
    exit 1
}

# 檢查必要檔案
if (Test-Path "app.py") {
    Write-Host "  ✅ 找到 app.py" -ForegroundColor Green
} else {
    Write-Host "  ❌ 找不到 app.py！請確認在正確的目錄" -ForegroundColor Red
    exit 1
}

# 檢查防火牆規則
Write-Host ""
Write-Host "🔥 檢查防火牆..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "*3000*" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "  ✅ 防火牆規則已設定" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  尚未設定防火牆規則" -ForegroundColor Yellow
    Write-Host "     建議執行（需要系統管理員）：" -ForegroundColor Gray
    Write-Host "     New-NetFirewallRule -DisplayName '藥物辨識系統 Port 3000' -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow" -ForegroundColor Gray
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 提示：" -ForegroundColor Cyan
Write-Host "  • 按 Ctrl+C 可停止伺服器" -ForegroundColor White
Write-Host "  • 詳細設定請查看 LOCAL_SERVER_SETUP.md" -ForegroundColor White
Write-Host "  • 想要讓外網也能訪問？使用 ngrok（見文檔）" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# 等待使用者確認
Write-Host "按任意鍵啟動伺服器..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "🚀 正在啟動 Flask 伺服器..." -ForegroundColor Green
Write-Host ""

# 啟動 Flask
python app.py
