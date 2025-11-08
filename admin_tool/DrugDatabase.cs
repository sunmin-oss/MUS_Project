using System;
using System.Data;
using System.Data.SQLite;
using System.Collections.Generic;

namespace DrugManagementSystem
{
    /// <summary>
    /// 藥物資料存取層
    /// </summary>
    public class DrugDatabase
    {
        private readonly string connectionString;

        public DrugDatabase(string dbPath)
        {
            connectionString = $"Data Source={dbPath};Version=3;";
        }

        /// <summary>
        /// 取得所有藥物資料
        /// </summary>
        public DataTable GetAllDrugs()
        {
            using var conn = new SQLiteConnection(connectionString);
            conn.Open();

            string query = @"
                SELECT 
                    id,
                    license_number AS 許可證字號,
                    chinese_name AS 中文品名,
                    english_name AS 英文品名,
                    shape AS 形狀,
                    special_dosage_form AS 特殊劑型,
                    color AS 顏色,
                    special_odor AS 特殊氣味,
                    mark AS 刻痕,
                    size AS 外觀尺寸,
                    label_front AS 標註一,
                    label_back AS 標註二,
                    indications AS 適應症,
                    dosage AS 用法用量,
                    side_effects AS 副作用,
                    contraindications AS 禁忌症,
                    precautions AS 注意事項,
                    ingredient AS 主要成分,
                    category AS 藥品分類,
                    manufacturer AS 製造商,
                    storage_conditions AS 儲存條件,
                    expiry_info AS 有效期限
                FROM drugs
                ORDER BY id";

            using var adapter = new SQLiteDataAdapter(query, conn);
            var table = new DataTable();
            adapter.Fill(table);
            return table;
        }

        /// <summary>
        /// 搜尋藥物（模糊比對）
        /// </summary>
        public DataTable SearchDrugs(string keyword, string? shape = null, string? color = null, string? month = null)
        {
            using var conn = new SQLiteConnection(connectionString);
            conn.Open();

            var conditions = new List<string>();
            var parameters = new List<SQLiteParameter>();

            if (!string.IsNullOrWhiteSpace(keyword))
            {
                conditions.Add("(license_number LIKE @keyword OR chinese_name LIKE @keyword OR english_name LIKE @keyword)");
                parameters.Add(new SQLiteParameter("@keyword", $"%{keyword}%"));
            }

            if (!string.IsNullOrWhiteSpace(shape) && shape != "全部劑型")
            {
                conditions.Add("shape LIKE @shape");
                parameters.Add(new SQLiteParameter("@shape", $"%{shape}%"));
            }

            if (!string.IsNullOrWhiteSpace(color) && color != "全部顏色")
            {
                conditions.Add("color LIKE @color");
                parameters.Add(new SQLiteParameter("@color", $"%{color}%"));
            }

            if (!string.IsNullOrWhiteSpace(month) && month != "全部月份")
            {
                // 假設有 updated_date 欄位，格式為 YYYYMM
                conditions.Add("substr(updated_date, 5, 2) = @month");
                parameters.Add(new SQLiteParameter("@month", month));
            }

            string whereClause = conditions.Count > 0 ? "WHERE " + string.Join(" AND ", conditions) : "";

            string query = $@"
                SELECT 
                    id,
                    license_number AS 許可證字號,
                    chinese_name AS 中文品名,
                    english_name AS 英文品名,
                    shape AS 形狀,
                    special_dosage_form AS 特殊劑型,
                    color AS 顏色,
                    special_odor AS 特殊氣味,
                    mark AS 刻痕,
                    size AS 外觀尺寸,
                    label_front AS 標註一,
                    label_back AS 標註二,
                    indications AS 適應症,
                    dosage AS 用法用量,
                    side_effects AS 副作用,
                    contraindications AS 禁忌症,
                    precautions AS 注意事項,
                    ingredient AS 主要成分,
                    category AS 藥品分類,
                    manufacturer AS 製造商,
                    storage_conditions AS 儲存條件,
                    expiry_info AS 有效期限
                FROM drugs
                {whereClause}
                ORDER BY id";

            using var cmd = new SQLiteCommand(query, conn);
            cmd.Parameters.AddRange(parameters.ToArray());

            using var adapter = new SQLiteDataAdapter(cmd);
            var table = new DataTable();
            adapter.Fill(table);
            return table;
        }

        /// <summary>
        /// 取得藥物圖片檔名列表
        /// </summary>
        public List<string> GetDrugImages(int drugId)
        {
            using var conn = new SQLiteConnection(connectionString);
            conn.Open();

            string query = "SELECT image_filename FROM drug_images WHERE drug_id = @drugId";
            using var cmd = new SQLiteCommand(query, conn);
            cmd.Parameters.AddWithValue("@drugId", drugId);

            var images = new List<string>();
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                images.Add(reader.GetString(0));
            }
            return images;
        }

        /// <summary>
        /// 新增藥物
        /// </summary>
        public int InsertDrug(string licenseNumber, string chineseName, string? englishName,
            string? shape, string? specialDosageForm, string? color, string? specialOdor,
            string? mark, string? size, string? labelFront, string? labelBack,
            string? indications, string? dosage, string? sideEffects, string? contraindications,
            string? precautions, string? ingredient, string? category, string? manufacturer,
            string? storageConditions, string? expiryInfo)
        {
            using var conn = new SQLiteConnection(connectionString);
            conn.Open();

            string query = @"
                INSERT INTO drugs (
                    license_number, chinese_name, english_name, shape, 
                    special_dosage_form, color, special_odor, mark, 
                    size, label_front, label_back,
                    indications, dosage, side_effects, contraindications,
                    precautions, ingredient, category, manufacturer,
                    storage_conditions, expiry_info
                ) VALUES (
                    @license_number, @chinese_name, @english_name, @shape,
                    @special_dosage_form, @color, @special_odor, @mark,
                    @size, @label_front, @label_back,
                    @indications, @dosage, @side_effects, @contraindications,
                    @precautions, @ingredient, @category, @manufacturer,
                    @storage_conditions, @expiry_info
                );
                SELECT last_insert_rowid();";

            using var cmd = new SQLiteCommand(query, conn);
            cmd.Parameters.AddWithValue("@license_number", licenseNumber);
            cmd.Parameters.AddWithValue("@chinese_name", chineseName);
            cmd.Parameters.AddWithValue("@english_name", englishName ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@shape", shape ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@special_dosage_form", specialDosageForm ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@color", color ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@special_odor", specialOdor ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@mark", mark ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@size", size ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@label_front", labelFront ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@label_back", labelBack ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@indications", indications ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@dosage", dosage ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@side_effects", sideEffects ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@contraindications", contraindications ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@precautions", precautions ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@ingredient", ingredient ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@category", category ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@manufacturer", manufacturer ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@storage_conditions", storageConditions ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@expiry_info", expiryInfo ?? (object)DBNull.Value);

            return Convert.ToInt32(cmd.ExecuteScalar());
        }

        /// <summary>
        /// 更新藥物
        /// </summary>
        public void UpdateDrug(int id, string licenseNumber, string chineseName, string? englishName,
            string? shape, string? specialDosageForm, string? color, string? specialOdor,
            string? mark, string? size, string? labelFront, string? labelBack,
            string? indications, string? dosage, string? sideEffects, string? contraindications,
            string? precautions, string? ingredient, string? category, string? manufacturer,
            string? storageConditions, string? expiryInfo)
        {
            using var conn = new SQLiteConnection(connectionString);
            conn.Open();

            string query = @"
                UPDATE drugs SET
                    license_number = @license_number,
                    chinese_name = @chinese_name,
                    english_name = @english_name,
                    shape = @shape,
                    special_dosage_form = @special_dosage_form,
                    color = @color,
                    special_odor = @special_odor,
                    mark = @mark,
                    size = @size,
                    label_front = @label_front,
                    label_back = @label_back,
                    indications = @indications,
                    dosage = @dosage,
                    side_effects = @side_effects,
                    contraindications = @contraindications,
                    precautions = @precautions,
                    ingredient = @ingredient,
                    category = @category,
                    manufacturer = @manufacturer,
                    storage_conditions = @storage_conditions,
                    expiry_info = @expiry_info
                WHERE id = @id";

            using var cmd = new SQLiteCommand(query, conn);
            cmd.Parameters.AddWithValue("@id", id);
            cmd.Parameters.AddWithValue("@license_number", licenseNumber);
            cmd.Parameters.AddWithValue("@chinese_name", chineseName);
            cmd.Parameters.AddWithValue("@english_name", englishName ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@shape", shape ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@special_dosage_form", specialDosageForm ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@color", color ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@special_odor", specialOdor ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@mark", mark ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@size", size ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@label_front", labelFront ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@label_back", labelBack ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@indications", indications ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@dosage", dosage ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@side_effects", sideEffects ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@contraindications", contraindications ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@precautions", precautions ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@ingredient", ingredient ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@category", category ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@manufacturer", manufacturer ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@storage_conditions", storageConditions ?? (object)DBNull.Value);
            cmd.Parameters.AddWithValue("@expiry_info", expiryInfo ?? (object)DBNull.Value);

            cmd.ExecuteNonQuery();
        }

        /// <summary>
        /// 刪除藥物（含關聯圖片記錄）
        /// </summary>
        public void DeleteDrug(int id)
        {
            using var conn = new SQLiteConnection(connectionString);
            conn.Open();

            using var transaction = conn.BeginTransaction();
            try
            {
                // 先刪除圖片記錄
                using (var cmd = new SQLiteCommand("DELETE FROM drug_images WHERE drug_id = @id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", id);
                    cmd.ExecuteNonQuery();
                }

                // 刪除藥物
                using (var cmd = new SQLiteCommand("DELETE FROM drugs WHERE id = @id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", id);
                    cmd.ExecuteNonQuery();
                }

                transaction.Commit();
            }
            catch
            {
                transaction.Rollback();
                throw;
            }
        }

        /// <summary>
        /// 取得所有形狀選項
        /// </summary>
        public List<string> GetShapeOptions()
        {
            using var conn = new SQLiteConnection(connectionString);
            conn.Open();

            string query = "SELECT DISTINCT shape FROM drugs WHERE shape IS NOT NULL AND shape != '' ORDER BY shape";
            using var cmd = new SQLiteCommand(query, conn);

            var shapes = new List<string> { "全部劑型" };
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                shapes.Add(reader.GetString(0));
            }
            return shapes;
        }

        /// <summary>
        /// 取得所有顏色選項
        /// </summary>
        public List<string> GetColorOptions()
        {
            using var conn = new SQLiteConnection(connectionString);
            conn.Open();

            string query = "SELECT DISTINCT color FROM drugs WHERE color IS NOT NULL AND color != '' ORDER BY color";
            using var cmd = new SQLiteCommand(query, conn);

            var colors = new List<string> { "全部顏色" };
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                colors.Add(reader.GetString(0));
            }
            return colors;
        }
    }
}
