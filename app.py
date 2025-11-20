"""
============================================================================
藥物辨識系統 - Flask 後端主程式 (app.py)
============================================================================

【專題說明】
這是一個基於影像辨識技術的藥物辨識系統，幫助使用者快速辨識藥物資訊。

【檔案功能】
此檔案是整個系統的核心後端服務，使用 Flask 框架提供 RESTful API 介面。
主要負責:
1. 接收前端上傳的藥物圖片
2. 呼叫影像辨識模組進行藥物辨識
3. 查詢資料庫取得藥物詳細資訊
4. 提供藥物名稱搜尋功能
5. 處理圖片上傳與儲存

【API 端點】
- GET  /api/test              - 測試 API 是否正常運作
- POST /api/search_by_name    - 根據藥物名稱搜尋
- POST /api/search_by_features - 根據外觀特徵(顏色/形狀)搜尋
- POST /api/recognize          - 上傳圖片進行藥物辨識
- GET  /api/drug/<id>          - 取得單一藥物詳細資訊
- GET  /api/images/<filename>  - 取得藥物圖片
- GET  /api/stats              - 取得系統統計資訊

【使用技術】
- Flask: Python Web 框架
- Flask-CORS: 處理跨網域請求
- SQLite: 資料庫
- OpenCV: 影像處理與特徵比對

【作者】MUS_Project 團隊
【日期】2024-2025
============================================================================
"""

from flask import Flask, jsonify, request, send_from_directory
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from flask_cors import CORS
from database_query import DrugDatabase
from image_recognition import DrugImageRecognizer, detect_image_type
import threading
import time
import uuid

app = Flask(__name__)
# 允許跨網域請求，特別允許 Vercel 網域
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "https://mus-project.vercel.app",
                "http://localhost:*",
                "http://127.0.0.1:*",
                "https://*.ngrok-free.dev",
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    },
)
DB_PATH = "drug_recognition.db"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp"}

# 確保上傳資料夾存在
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# 初始化影像辨識器
feature_recognizer = DrugImageRecognizer(DB_PATH)

# 延遲載入 OCR（避免啟動時間過長，因為 OCR 模型較大）
ocr_recognizer = None

# 簡易進度/取消管理 (用於追蹤辨識進度)
PROGRESS = {}  # request_id -> {done:int, total:int, status:str, ts:float}
CANCEL_FLAGS = {}  # request_id -> threading.Event


def get_ocr_recognizer():
    """
    獲取 OCR 辨識器（延遲載入）

    說明:
    - OCR 模型較大，延遲載入可加快系統啟動速度
    - 只有在使用者真正需要 OCR 功能時才載入
    - 使用全域變數快取，避免重複載入

    Returns:
        DrugOCRRecognizer 實例，載入失敗則返回 None
    """
    global ocr_recognizer
    if ocr_recognizer is None:
        try:
            from ocr_module import DrugOCRRecognizer

            ocr_recognizer = DrugOCRRecognizer(DB_PATH)
        except Exception as e:
            print(f"⚠️  OCR 模組載入失敗: {e}")
            ocr_recognizer = False  # 標記為失敗，避免重複嘗試
    return ocr_recognizer if ocr_recognizer is not False else None


@app.route("/api/search/name", methods=["GET"])
def search_by_name():
    """
    藥物名稱模糊搜尋 API

    功能:
    - 根據藥物中文名稱或英文名稱進行模糊搜尋
    - 支援部分匹配 (例如: 輸入"普拿"可找到"普拿疼")
    - 支援字形變體 (例如: 輸入"阿斯匹靈"可找到"阿斯匹林")

    參數 (Query String):
        q (str): 搜尋關鍵字
        limit (int): 最多回傳筆數，預設 20

    回傳:
        JSON: {
            "success": bool,
            "count": int,
            "data": [藥物資訊列表]
        }

    範例:
        GET /api/search/name?q=普拿疼&limit=10
    """
    query = request.args.get("q", "")
    limit = int(request.args.get("limit", 20))

    print(f"收到搜尋請求: {query}")  # 除錯訊息

    with DrugDatabase(DB_PATH) as db:
        results = db.search_by_name(query, limit)
        print(f"找到 {len(results)} 筆資料")  # 除錯訊息

        # 為每個藥物加入圖片資訊
        for drug in results:
            images = db.get_drug_images(drug["id"])
            drug["images"] = images
            print(f"藥物 {drug['chinese_name']} 有 {len(images)} 張圖片")  # 除錯訊息

        return jsonify({"success": True, "count": len(results), "data": results})


@app.route("/api/search/features", methods=["GET"])
def search_by_features():
    """
    藥物外觀特徵搜尋 API

    功能:
    - 根據藥物的外觀特徵進行搜尋 (形狀、顏色、標記)
    - 支援多條件組合搜尋
    - 可搭配文字搜尋使用

    參數 (Query String):
        q (str): 文字搜尋關鍵字 (選填)
        color (str): 藥物顏色 (選填，例如: "白色", "紅色")
        label (str): 藥物標記/刻痕 (選填，例如: "圓形", "十字")
        limit (int): 最多回傳筆數，預設 20

    回傳:
        JSON: {
            "success": bool,
            "count": int,
            "data": [藥物資訊列表]
        }

    範例:
        GET /api/search/features?color=白色&label=圓形&limit=10
    """
    query = request.args.get("q", "").strip()
    color = request.args.get("color")
    label = request.args.get("label")
    limit = int(request.args.get("limit", 20))
    with DrugDatabase(DB_PATH) as db:
        results = db.search_by_features(query, color, label, limit)
        return jsonify({"success": True, "count": len(results), "data": results})


@app.route("/api/drug/<int:drug_id>", methods=["GET"])
def get_drug_with_images(drug_id):
    """
    取得指定藥物的所有欄位與圖片 API

    功能:
    - 根據藥物 ID 獲取完整的藥物資訊
    - 包含所有資料庫欄位 (中英文名稱、外觀、臨床資訊等)
    - 自動附加所有關聯的藥物圖片

    參數 (URL 路徑):
        drug_id (int): 藥物 ID

    回傳:
        JSON: {
            "success": bool,
            "data": {藥物完整資訊, 包含 images 陣列}
        }
        或 404 錯誤 (查無此藥物)

    範例:
        GET /api/drug/123
    """
    with DrugDatabase(DB_PATH) as db:
        drug = db.get_drug(drug_id)
        if not drug:
            return jsonify({"success": False, "message": "查無此藥物"}), 404
        images = db.get_drug_images(drug_id)
        drug["images"] = images
        return jsonify({"success": True, "data": drug})


def get_drug_detail(drug_id):
    """
    取得藥物詳細資訊 API (內部使用)

    說明:
    - 此函數為內部輔助函數，整合藥物基本資訊與圖片
    - 與 get_drug_with_images 功能類似，但使用不同的資料庫方法

    參數:
        drug_id (int): 藥物 ID

    回傳:
        JSON 回應物件
    """
    with DrugDatabase(DB_PATH) as db:
        drug = db.get_drug_with_images(drug_id)
        if drug:
            return jsonify({"success": True, "data": drug})
        else:
            return jsonify({"success": False, "error": "藥物不存在"}), 404


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """
    取得資料庫統計資訊 API

    功能:
    - 回傳資料庫的各項統計數據
    - 包含藥物總數、圖片總數、特徵分佈等

    回傳:
        JSON: {
            "success": bool,
            "data": {統計資訊物件}
        }

    範例:
        GET /api/statistics
    """
    with DrugDatabase(DB_PATH) as db:
        stats = db.get_statistics()
        return jsonify({"success": True, "data": stats})


def allowed_file(filename):
    """
    檢查檔案類型是否允許

    功能:
    - 驗證上傳的檔案是否為允許的圖片格式
    - 支援格式: png, jpg, jpeg, gif, bmp

    參數:
        filename (str): 檔案名稱

    回傳:
        bool: True 表示允許，False 表示不允許
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/recognize", methods=["POST"])
def recognize_drug():
    """
    藥物圖片辨識 API (支援多種模型)

    功能:
    - 接受上傳的藥物圖片，使用指定的辨識模型進行分析
    - 支援影像特徵辨識、OCR 文字辨識、處方籤辨識等模式
    - 回傳最相似的 Top-K 藥物候選清單

    支援的辨識模式:
    1. auto (自動) - 系統自動選擇最適合的模型
    2. feature (特徵) - 使用 OpenCV 影像特徵比對 (顏色、形狀、紋理、刻痕)
    3. ocr (文字) - 使用 PaddleOCR 辨識藥物上的文字標記
    4. prescription (處方籤) - 辨識處方籤上的藥物名稱

    參數 (Form Data):
        image (File): 上傳的圖片檔案 (必填)
        model (str): 辨識模式，預設 "auto"
        top_k (int): 回傳前 K 名候選，預設 5
        request_id (str): 請求 ID，用於追蹤進度與取消 (選填)

    回傳:
        JSON: {
            "success": bool,
            "data": [辨識結果陣列],
            "model_used": str,
            "request_id": str
        }
        或錯誤訊息 (400/500)

    範例:
        POST /api/recognize
        Form-Data: image=<file>, model="feature", top_k=10
    """
    # 檢查是否有檔案
    if "image" not in request.files:
        return jsonify({"success": False, "message": "未上傳圖片"}), 400

    file = request.files["image"]

    # 檢查檔案名稱
    if file.filename == "":
        return jsonify({"success": False, "message": "未選擇檔案"}), 400

    # 檢查檔案類型
    if not allowed_file(file.filename):
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"不支援的檔案格式，請上傳 {', '.join(ALLOWED_EXTENSIONS)} 格式",
                }
            ),
            400,
        )

    try:
        # 安全的檔案名稱 (防止路徑穿越攻擊)
        filename = secure_filename(file.filename)
        # 加上時間戳避免檔名衝突
        import time

        timestamp = int(time.time())
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 儲存檔案到伺服器
        file.save(filepath)

        # 獲取辨識參數
        model_type = request.form.get(
            "model", "auto"
        )  # auto, feature, ocr, prescription
        top_k = int(request.form.get("top_k", 5))

        # 請求識別 ID（用於追蹤進度與支援取消功能）
        request_id = request.form.get("request_id") or uuid.uuid4().hex

        # 自動判斷模型（現在統一使用特徵比對）
        if model_type == "auto":
            model_type = "feature"  # 統一使用特徵比對
            print(f"🤖 使用影像特徵比對模式")

        # 強制使用特徵比對（移除 OCR 和藥單模式）
        if model_type in ["ocr", "prescription"]:
            model_type = "feature"
            print(f"⚠️  已將模式改為影像特徵比對")

        # 特徵比對模式
        # 獲取形狀和顏色過濾條件
        filter_shape = request.form.get("shape", "").strip() or None
        filter_color = request.form.get("color", "").strip() or None

        # 初始化進度與取消旗標
        cancel_ev = threading.Event()
        CANCEL_FLAGS[request_id] = cancel_ev
        PROGRESS[request_id] = {
            "done": 0,
            "total": 0,
            "status": "running",
            "ts": time.time(),
        }

        def on_progress(done, total):
            PROGRESS[request_id] = {
                "done": int(done),
                "total": int(total),
                "status": "running",
                "ts": time.time(),
            }

        def is_cancelled():
            return cancel_ev.is_set()

        try:
            # 呼叫辨識器並套用篩選（帶入 hooks）
            results = feature_recognizer.recognize_drug(
                filepath,
                top_k=top_k,
                filter_shape=filter_shape,
                filter_color=filter_color,
                hooks={"on_progress": on_progress, "is_cancelled": is_cancelled},
            )
            PROGRESS[request_id]["status"] = (
                "done" if not cancel_ev.is_set() else "canceled"
            )
        finally:
            # 清理取消旗標（保留進度一段時間供前端讀取）
            CANCEL_FLAGS.pop(request_id, None)

        # 清理檔案
        Path(filepath).unlink(missing_ok=True)

        if not results:
            filter_msg = []
            if filter_shape:
                filter_msg.append(f"形狀: {filter_shape}")
            if filter_color:
                filter_msg.append(f"顏色: {filter_color}")

            if filter_msg:
                return jsonify(
                    {
                        "success": False,
                        "message": f"找不到符合條件的藥物 ({', '.join(filter_msg)})，請調整篩選條件或重新拍照",
                    }
                )
            else:
                return jsonify(
                    {
                        "success": False,
                        "message": "無法辨識，請確保圖片清晰且包含完整藥物",
                    }
                )

        # 補充完整藥物資訊
        enriched_results = []
        with DrugDatabase(DB_PATH) as db:
            for result in results:
                drug = db.get_drug(result["drug_id"])
                if drug:
                    enriched_result = {
                        **drug,
                        "similarity": result["similarity"],
                        "similarity_percent": result["similarity_percent"],
                    }
                    images = db.get_drug_images(result["drug_id"])
                    enriched_result["images"] = images
                    enriched_results.append(enriched_result)

        return jsonify(
            {
                "success": True,
                "method": "特徵比對",
                "request_id": request_id,
                "filters": {
                    "shape": filter_shape,
                    "color": filter_color,
                },
                "count": len(enriched_results),
                "data": enriched_results,
            }
        )

    except Exception as e:
        # 清理可能存在的上傳檔案
        if "filepath" in locals():
            Path(filepath).unlink(missing_ok=True)

        return (
            jsonify({"success": False, "message": f"辨識過程發生錯誤: {str(e)}"}),
            500,
        )


@app.route("/api/cancel", methods=["POST"])
def cancel_request():
    """
    取消辨識請求 API

    功能:
    - 允許使用者中途取消正在進行的辨識任務
    - 透過 request_id 標識要取消的請求
    - 使用 threading.Event 機制通知辨識執行緒停止

    參數 (JSON Body):
        request_id (str): 要取消的請求 ID (必填)

    回傳:
        JSON: {
            "success": bool,
            "message": str
        }

    說明:
    - 如果請求已完成或不存在，仍回傳成功以簡化前端邏輯
    - 取消後進度狀態會更新為 "canceled"

    範例:
        POST /api/cancel
        Body: {"request_id": "abc123def456"}
    """
    data = request.get_json(silent=True) or {}
    req_id = data.get("request_id")
    if not req_id:
        return jsonify({"success": False, "message": "缺少 request_id"}), 400
    ev = CANCEL_FLAGS.get(req_id)
    if not ev:
        # 若找不到也回成功，讓前端流程簡單
        PROGRESS[req_id] = {
            "done": 0,
            "total": 0,
            "status": "canceled",
            "ts": time.time(),
        }
        return jsonify({"success": True, "message": "not running or already finished"})

    # 設定取消旗標，通知辨識執行緒停止
    ev.set()
    PROGRESS[req_id] = {
        "done": PROGRESS.get(req_id, {}).get("done", 0),
        "total": PROGRESS.get(req_id, {}).get("total", 0),
        "status": "canceled",
        "ts": time.time(),
    }
    return jsonify({"success": True})


@app.route("/api/progress/<request_id>", methods=["GET"])
def get_progress(request_id):
    """
    查詢辨識進度 API

    功能:
    - 即時查詢指定 request_id 的辨識進度
    - 用於前端顯示進度條或狀態提示

    參數 (URL 路徑):
        request_id (str): 請求 ID

    回傳:
        JSON: {
            "success": bool,
            "status": str,  # "running", "done", "canceled", "unknown"
            "done": int,    # 已完成數量
            "total": int,   # 總數量
            "ts": float     # 時間戳
        }

    範例:
        GET /api/progress/abc123def456
    """
    info = PROGRESS.get(request_id)
    if not info:
        return jsonify({"success": False, "status": "unknown", "done": 0, "total": 0})
    return jsonify({"success": True, **info})


# ============================================================================
# 靜態檔案服務與前端路由
# ============================================================================


@app.route("/images/<path:filename>")
def serve_image(filename):
    """
    提供藥物圖片靜態檔案服務

    功能:
    - 允許前端透過 URL 直接存取 medicine_photos 資料夾內的圖片
    - 用於顯示搜尋結果、辨識結果中的藥物圖片

    參數 (URL 路徑):
        filename (str): 圖片檔名 (支援子路徑)

    範例:
        GET /images/阿斯匹靈_1.jpg
    """
    return send_from_directory("medicine_photos", filename)


@app.route("/")
def index():
    """
    提供前端首頁 (index.html)

    功能:
    - 作為 Web 應用的入口點
    - 提供使用者介面 (藥物搜尋、圖片辨識等功能)
    """
    return send_from_directory(".", "index.html")


# ============================================================================
# SEO 與維運相關端點
# ============================================================================


@app.route("/health")
def health():
    """
    健康檢查端點

    功能:
    - 用於監控系統是否正常運作
    - 適用於負載平衡器、容器編排系統 (如 Kubernetes) 的健康檢查

    回傳:
        JSON: {"status": "ok"}
    """
    return jsonify({"status": "ok"}), 200


@app.route("/robots.txt")
def robots_txt():
    """
    提供搜尋引擎爬蟲規則檔案

    功能:
    - 告知搜尋引擎哪些頁面可以爬取、哪些應避免
    - 改善 SEO 並保護敏感頁面
    """
    # 專案根目錄的 robots.txt
    return send_from_directory(".", "robots.txt", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    """
    提供網站地圖 (Sitemap) 檔案

    功能:
    - 幫助搜尋引擎更有效地爬取和索引網站內容
    - 列出網站中所有重要頁面的 URL
    - 提升 SEO 排名
    """
    # 專案根目錄的 sitemap.xml
    return send_from_directory(".", "sitemap.xml", mimetype="application/xml")


# ============================================================================
# 主程式入口
# ============================================================================

if __name__ == "__main__":
    """
    Flask 應用程式啟動入口

    功能:
    1. 檢查資料庫是否存在，若不存在則自動初始化
    2. 從環境變數讀取 PORT (適用於雲端平台如 Render)
    3. 啟動 Flask 伺服器，監聽所有網路介面 (0.0.0.0)

    部署說明:
    - 本地開發: 預設使用 port 3000
    - Render 部署: 使用環境變數 PORT
    - debug=False: 生產環境模式，避免暴露敏感資訊
    - use_reloader=False: 關閉自動重載，避免多執行緒問題
    """
    print("啟動 Flask 伺服器...")

    # 若資料庫不存在,嘗試以 CSV 初始化 (Render 首次部署常見情境)
    if not os.path.exists(DB_PATH):
        try:
            print(f"偵測不到資料庫 {DB_PATH},嘗試初始化...")
            from create_database import main as init_db

            init_db()
            print("資料庫初始化完成。")
        except Exception as e:
            print(f"初始化資料庫失敗(將以空資料庫啟動): {e}")

    # 對外提供服務請使用 0.0.0.0; Render 會提供 PORT 環境變數
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)
