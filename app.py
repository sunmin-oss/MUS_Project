from flask import Flask, jsonify, request, send_from_directory
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from flask_cors import CORS
from database_query import DrugDatabase
from image_recognition import DrugImageRecognizer, detect_image_type

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

# 初始化辨識器
feature_recognizer = DrugImageRecognizer(DB_PATH)

# 延遲載入 OCR（避免啟動時間過長）
ocr_recognizer = None


def get_ocr_recognizer():
    """獲取 OCR 辨識器（延遲載入）"""
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
    """藥物名稱模糊搜尋 API"""
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
    """藥物外觀特徵搜尋 API"""
    query = request.args.get("q", "").strip()
    color = request.args.get("color")
    label = request.args.get("label")
    limit = int(request.args.get("limit", 20))
    with DrugDatabase(DB_PATH) as db:
        results = db.search_by_features(query, color, label, limit)
        return jsonify({"success": True, "count": len(results), "data": results})


@app.route("/api/drug/<int:drug_id>", methods=["GET"])
def get_drug_with_images(drug_id):
    """取得指定藥物的所有欄位與圖片 API"""
    with DrugDatabase(DB_PATH) as db:
        drug = db.get_drug(drug_id)
        if not drug:
            return jsonify({"success": False, "message": "查無此藥物"}), 404
        images = db.get_drug_images(drug_id)
        drug["images"] = images
        return jsonify({"success": True, "data": drug})


def get_drug_detail(drug_id):
    """取得藥物詳細資訊 API"""
    with DrugDatabase(DB_PATH) as db:
        drug = db.get_drug_with_images(drug_id)
        if drug:
            return jsonify({"success": True, "data": drug})
        else:
            return jsonify({"success": False, "error": "藥物不存在"}), 404


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    """取得資料庫統計資訊 API"""
    with DrugDatabase(DB_PATH) as db:
        stats = db.get_statistics()
        return jsonify({"success": True, "data": stats})


def allowed_file(filename):
    """檢查檔案類型是否允許"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/recognize", methods=["POST"])
def recognize_drug():
    """
    藥物圖片辨識 API（支援多種模型）
    接受上傳的藥物圖片，返回辨識結果
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
        # 安全的檔案名稱
        filename = secure_filename(file.filename)
        # 加上時間戳避免重複
        import time

        timestamp = int(time.time())
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # 儲存檔案
        file.save(filepath)

        # 獲取參數
        model_type = request.form.get(
            "model", "auto"
        )  # auto, feature, ocr, prescription
        top_k = int(request.form.get("top_k", 5))

        # 自動判斷模型
        if model_type == "auto":
            image_type = detect_image_type(filepath)
            if image_type == "text":
                model_type = "ocr"
                print(f"🤖 自動選擇：OCR 模式（檢測到文字內容）")
            elif image_type == "object":
                model_type = "feature"
                print(f"🤖 自動選擇：影像特徵模式（檢測到單一物體）")
            else:
                model_type = "feature"  # 預設使用特徵比對
                print(f"🤖 自動選擇：影像特徵模式（預設）")

        # 根據模型類型執行辨識
        if model_type == "ocr":
            # OCR 模式
            ocr = get_ocr_recognizer()
            if ocr is None:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "OCR 模組未安裝，請執行：pip install paddleocr paddlepaddle",
                        }
                    ),
                    500,
                )

            result = ocr.recognize_single_drug_name(filepath)

            # 清理檔案
            Path(filepath).unlink(missing_ok=True)

            return jsonify(result)

        elif model_type == "prescription":
            # 藥單模式（OCR）
            ocr = get_ocr_recognizer()
            if ocr is None:
                return jsonify({"success": False, "message": "OCR 模組未安裝"}), 500

            result = ocr.recognize_prescription(filepath)

            # 清理檔案
            Path(filepath).unlink(missing_ok=True)

            return jsonify(result)

        else:
            # 特徵比對模式（預設）
            results = feature_recognizer.recognize_drug(filepath, top_k=top_k)

            # 清理檔案
            Path(filepath).unlink(missing_ok=True)

            if not results:
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


# 圖片靜態檔案服務
@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory("medicine_photos", filename)


# 提供前端頁面
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# SEO/ops endpoints
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/robots.txt")
def robots_txt():
    # 專案根目錄的 robots.txt
    return send_from_directory(".", "robots.txt", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap_xml():
    # 專案根目錄的 sitemap.xml
    return send_from_directory(".", "sitemap.xml", mimetype="application/xml")


if __name__ == "__main__":
    print("啟動 Flask 伺服器...")
    # 若資料庫不存在，嘗試以 CSV 初始化（Render 首次部署常見情境）
    if not os.path.exists(DB_PATH):
        try:
            print(f"偵測不到資料庫 {DB_PATH}，嘗試初始化...")
            from create_database import main as init_db

            init_db()
            print("資料庫初始化完成。")
        except Exception as e:
            print(f"初始化資料庫失敗（將以空資料庫啟動）：{e}")

    # 對外提供服務請使用 0.0.0.0；Render 會提供 PORT 環境變數
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)
