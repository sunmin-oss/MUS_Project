# ngrok 互動式設定助手

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ngrok 設定助手" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: 檢查是否已安裝 ngrok
Write-Host "🔍 Step 1: 檢查 ngrok 安裝狀態..." -ForegroundColor Yellow
Write-Host ""

try {
    $ngrokPath = (Get-Command ngrok -ErrorAction Stop).Source
    Write-Host "  ✅ 已找到 ngrok！" -ForegroundColor Green
    Write-Host "  📍 位置: $ngrokPath" -ForegroundColor White
    Write-Host ""
    
    # 測試版本
    $version = ngrok version 2>&1
    Write-Host "  📦 版本: $version" -ForegroundColor White
    Write-Host ""
    
    $ngrokInstalled = $true
} catch {
    Write-Host "  ❌ 尚未安裝或未加入 PATH" -ForegroundColor Red
    Write-Host ""
    $ngrokInstalled = $false
}

# Step 2: 如果未安裝，提供指引
if (-not $ngrokInstalled) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📥 請按照以下步驟安裝 ngrok：" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. 前往下載頁面：" -ForegroundColor White
    Write-Host "     https://ngrok.com/download" -ForegroundColor Blue
    Write-Host ""
    Write-Host "  2. 點擊 'Windows (64-bit)' 下載" -ForegroundColor White
    Write-Host ""
    Write-Host "  3. 解壓縮 zip 檔案到 C:\ngrok\" -ForegroundColor White
    Write-Host "     （或任意資料夾）" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  4. 將 ngrok.exe 所在資料夾加入 PATH" -ForegroundColor White
    Write-Host "     或使用完整路徑執行" -ForegroundColor Gray
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    
    # 提供手動設定選項
    Write-Host "💡 如果您已經下載但未解壓縮：" -ForegroundColor Yellow
    Write-Host ""
    
    $downloadsPath = "$env:USERPROFILE\Downloads"
    $zipFiles = Get-ChildItem -Path $downloadsPath -Filter "*ngrok*.zip" -ErrorAction SilentlyContinue
    
    if ($zipFiles) {
        Write-Host "  找到 ngrok zip 檔案：" -ForegroundColor Green
        foreach ($zip in $zipFiles) {
            Write-Host "  📦 $($zip.Name)" -ForegroundColor White
        }
        Write-Host ""
        Write-Host "  請手動解壓縮檔案到 C:\ngrok\ 然後重新執行此腳本" -ForegroundColor Cyan
    } else {
        Write-Host "  在下載資料夾找不到 ngrok zip 檔案" -ForegroundColor Gray
        Write-Host "  請先從 https://ngrok.com/download 下載" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "完成下載和解壓縮後，請重新執行此腳本！" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "按任意鍵結束..." -ForegroundColor White
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Step 3: 檢查 authtoken
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "🔑 Step 2: 檢查 authtoken 設定..." -ForegroundColor Yellow
Write-Host ""

$configPath = "$env:USERPROFILE\.ngrok2\ngrok.yml"

if (Test-Path $configPath) {
    $hasToken = Select-String -Path $configPath -Pattern "authtoken:" -Quiet
    
    if ($hasToken) {
        Write-Host "  ✅ authtoken 已設定！" -ForegroundColor Green
        Write-Host ""
        $authtokenConfigured = $true
    } else {
        Write-Host "  ⚠️  設定檔存在但未找到 authtoken" -ForegroundColor Yellow
        Write-Host ""
        $authtokenConfigured = $false
    }
} else {
    Write-Host "  ⚠️  尚未設定 authtoken" -ForegroundColor Yellow
    Write-Host ""
    $authtokenConfigured = $false
}

# Step 4: 如果未設定 authtoken，提供指引
if (-not $authtokenConfigured) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📝 請設定您的 ngrok authtoken：" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. 登入 ngrok 控制台：" -ForegroundColor White
    Write-Host "     https://dashboard.ngrok.com/" -ForegroundColor Blue
    Write-Host ""
    Write-Host "  2. 點擊左側選單的 'Your Authtoken'" -ForegroundColor White
    Write-Host ""
    Write-Host "  3. 複製顯示的 authtoken" -ForegroundColor White
    Write-Host ""
    Write-Host "  4. 在 PowerShell 執行：" -ForegroundColor White
    Write-Host "     ngrok config add-authtoken <貼上您的token>" -ForegroundColor Gray
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    
    # 提供互動式輸入
    Write-Host "💡 或者現在就輸入您的 authtoken：" -ForegroundColor Yellow
    Write-Host ""
    $token = Read-Host "請貼上您的 authtoken (按 Enter 跳過)"
    
    if ($token) {
        Write-Host ""
        Write-Host "正在設定 authtoken..." -ForegroundColor Yellow
        
        try {
            $output = ngrok config add-authtoken $token 2>&1
            Write-Host "  ✅ authtoken 設定成功！" -ForegroundColor Green
            Write-Host ""
            $authtokenConfigured = $true
        } catch {
            Write-Host "  ❌ 設定失敗：$_" -ForegroundColor Red
            Write-Host ""
        }
    } else {
        Write-Host ""
        Write-Host "已跳過 authtoken 設定" -ForegroundColor Gray
        Write-Host "請稍後手動執行：ngrok config add-authtoken <token>" -ForegroundColor Gray
        Write-Host ""
        Write-Host "按任意鍵結束..." -ForegroundColor White
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit
    }
}

# Step 5: 全部設定完成
if ($ngrokInstalled -and $authtokenConfigured) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🎉 恭喜！ngrok 已經完全設定好了！" -ForegroundColor Green
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🚀 現在您可以啟動藥物辨識系統：" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  方法 1（推薦）：使用一鍵啟動腳本" -ForegroundColor White
    Write-Host "    .\start_with_ngrok.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  方法 2：手動啟動" -ForegroundColor White
    Write-Host "    視窗 1: python app.py" -ForegroundColor Gray
    Write-Host "    視窗 2: ngrok http 3000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    
    # 詢問是否立即啟動
    $launch = Read-Host "要立即啟動系統嗎？(Y/N)"
    
    if ($launch -eq "Y" -or $launch -eq "y") {
        Write-Host ""
        Write-Host "正在啟動系統..." -ForegroundColor Green
        Write-Host ""
        
        # 切換到專案目錄
        $projectPath = "d:\大學\專題\MUS_Project"
        Set-Location $projectPath
        
        # 執行啟動腳本
        & ".\start_with_ngrok.ps1"
    } else {
        Write-Host ""
        Write-Host "好的！稍後可以手動執行 start_with_ngrok.ps1 啟動" -ForegroundColor Cyan
        Write-Host ""
    }
}

Write-Host ""
Write-Host "按任意鍵關閉..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
