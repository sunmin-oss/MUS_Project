from flask import Flask, jsonify, request, send_from_directory
import os
from flask_cors import CORS
from database_query import DrugDatabase

app = Flask(__name__)
CORS(app)  # 允許跨網域請求（供前端獨立部署時使用）
DB_PATH = "drug_recognition.db"


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


# 圖片靜態檔案服務
@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory("medicine_photos", filename)


# 提供前端頁面
@app.route("/")
def index():
    return send_from_directory("drug-recognition-demo", "index.html")


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
    print("測試資料庫連線...")
    with DrugDatabase(DB_PATH) as db:
        test_results = db.search_by_name("建功丸")
        print(f"測試查詢: 找到 {len(test_results)} 筆建功丸資料")
        if len(test_results) > 0:
            test_images = db.get_drug_images(test_results[0]["id"])
            print(f"測試圖片: 建功丸有 {len(test_images)} 張圖片")

    # 對外提供服務請使用 0.0.0.0；Render 會提供 PORT 環境變數
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=False, use_reloader=False, host="0.0.0.0", port=port)
