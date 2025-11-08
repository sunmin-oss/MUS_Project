# 藥物資料管理系統啟動腳本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  藥物資料管理系統 (Drug Management System)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 .NET SDK
Write-Host "檢查 .NET SDK..." -ForegroundColor Yellow
$dotnetVersion = dotnet --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "錯誤: 找不到 .NET SDK" -ForegroundColor Red
    Write-Host "請從 https://dotnet.microsoft.com/download 下載安裝" -ForegroundColor Red
    exit 1
}
Write-Host "✓ .NET SDK $dotnetVersion" -ForegroundColor Green
Write-Host ""

# 切換到專案目錄
$projectRoot = "d:\大學\專題\MUS_Project"
$adminToolPath = Join-Path $projectRoot "admin_tool"

Set-Location $adminToolPath

# 檢查資料庫
$dbPath = Join-Path $projectRoot "drug_recognition.db"
if (-Not (Test-Path $dbPath)) {
    Write-Host "警告: 找不到資料庫檔案 $dbPath" -ForegroundColor Red
    Write-Host "請確認資料庫檔案存在後再執行" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 找到資料庫檔案" -ForegroundColor Green

# 檢查圖片資料夾
$photoDir = Join-Path $projectRoot "medicine_photos"
if (-Not (Test-Path $photoDir)) {
    Write-Host "警告: 找不到圖片資料夾 $photoDir" -ForegroundColor Yellow
    Write-Host "部分功能可能無法正常使用" -ForegroundColor Yellow
} else {
    Write-Host "✓ 找到圖片資料夾" -ForegroundColor Green
}
Write-Host ""

# 建置專案
Write-Host "建置專案..." -ForegroundColor Yellow
dotnet build --configuration Release --verbosity quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "錯誤: 建置失敗" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 建置成功" -ForegroundColor Green
Write-Host ""

# 執行程式
Write-Host "啟動管理系統..." -ForegroundColor Yellow
Write-Host ""
dotnet run --no-build --configuration Release
