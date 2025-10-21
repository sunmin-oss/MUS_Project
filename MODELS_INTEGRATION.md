# 多模型整合指南

## 已整合的模型

### 1. 影像特徵比對（預設，已啟用）
- **技術**：OpenCV 顏色直方圖 + 形狀特徵
- **優勢**：無需額外依賴，快速，適合單藥物照片
- **準確度**：中等（依賴資料庫圖片質量）
- **使用場景**：使用者拍攝清晰的單顆藥物照片

### 2. OCR 文字辨識（可選）
- **技術**：PaddleOCR 繁體中文模型
- **優勢**：可識別藥袋、藥盒、處方籤上的文字
- **準確度**：高（對清晰文字）
- **使用場景**：
  - 藥袋/藥盒上的藥名
  - 處方籤/藥單
  - 包含文字的藥物包裝

**安裝方式：**
```bash
pip install paddleocr paddlepaddle
```

## API 使用方式

### POST `/api/recognize`

**參數：**
- `image`：圖片檔案（必需）
- `model`：辨識模型選擇（選填）
  - `auto`：自動判斷（推薦）
  - `feature`：影像特徵比對
  - `ocr`：文字辨識
  - `prescription`：藥單模式（多藥物 OCR）
- `top_k`：返回前 K 個結果（預設 5）

**範例：**

```bash
# 自動模式（推薦）
curl -X POST http://localhost:3000/api/recognize \
  -F "image=@drug_photo.jpg" \
  -F "model=auto"

# OCR 模式
curl -X POST http://localhost:3000/api/recognize \
  -F "image=@prescription.jpg" \
  -F "model=ocr"

# 藥單模式
curl -X POST http://localhost:3000/api/recognize \
  -F "image=@prescription.jpg" \
  -F "model=prescription"
```

## 自動模式判斷邏輯

系統會自動分析圖片特徵：
- **文字密度高 + 小輪廓多** → 使用 OCR
- **輪廓少 + 邊緣密度低** → 使用影像特徵
- **其他情況** → 預設使用影像特徵

## 未來可整合的模型

### 3. 藥丸影像分類模型（計劃中）
- **資料集**：NLM Pill Dataset / Drug Pills Image Database
- **技術**：ResNet / EfficientNet 遷移學習
- **優勢**：專門針對藥丸外觀訓練，準確度更高
- **實作方式**：
  1. 下載預訓練模型或自行訓練
  2. 整合到 `pill_model.py`
  3. 在 API 中加入 `model=pill` 選項

### 4. YOLO 物體檢測（計劃中）
- **用途**：藥單多藥物檢測與定位
- **優勢**：可同時檢測多個藥物並框選
- **整合後功能**：
  - 自動裁切每個藥物區域
  - 分別對各區域進行辨識
  - 返回帶座標的結果

## 模型效能比較

| 模型 | 準確度 | 速度 | 依賴大小 | 適用場景 |
|------|--------|------|----------|----------|
| 影像特徵 | ⭐⭐⭐ | ⚡⚡⚡ | 小 | 單藥物清晰照片 |
| OCR | ⭐⭐⭐⭐ | ⚡⚡ | 大 (~500MB) | 文字清晰的藥袋/處方 |
| Pill 模型 | ⭐⭐⭐⭐⭐ | ⚡⚡ | 中 | 單藥丸特寫 |
| YOLO | ⭐⭐⭐⭐ | ⚡ | 大 | 多藥物同時檢測 |

## 開發建議

1. **本地開發**：
   - 預設使用影像特徵（無需額外依賴）
   - 需要測試 OCR 時再安裝 PaddleOCR

2. **生產環境**：
   - Render 免費方案記憶體有限，建議僅部署影像特徵模型
   - 如需 OCR，考慮升級方案或使用雲端 API

3. **準確度提升**：
   - 收集更多台灣藥物圖片充實資料庫
   - 訓練專用的台灣藥物辨識模型
   - 結合多個模型的結果（ensemble）

## 貢獻指南

歡迎貢獻新的模型整合：

1. 在 `models/` 資料夾建立新的模型模組
2. 實作 `recognize()` 介面
3. 在 `app.py` 加入路由選項
4. 更新此文件說明
5. 提供測試範例

## 參考資源

- **PaddleOCR**: https://github.com/PaddlePaddle/PaddleOCR
- **NLM Pill Dataset**: https://www.mdpi.com/article
- **Drug Pills Database**: https://ietresearch.onlinelibrary.wiley.com/
- **中文 OCR 資料集**: https://github.com/FudanVI/benchmarking-chinese-text-recognition
