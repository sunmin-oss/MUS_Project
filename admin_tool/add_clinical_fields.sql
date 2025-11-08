-- 為 drugs 資料表新增臨床欄位
-- 執行方式: sqlite3 drug_recognition.db < add_clinical_fields.sql

-- 新增適應症欄位
ALTER TABLE drugs ADD COLUMN indications TEXT;

-- 新增用法用量欄位
ALTER TABLE drugs ADD COLUMN dosage TEXT;

-- 新增副作用欄位
ALTER TABLE drugs ADD COLUMN side_effects TEXT;

-- 新增禁忌症欄位
ALTER TABLE drugs ADD COLUMN contraindications TEXT;

-- 新增注意事項欄位
ALTER TABLE drugs ADD COLUMN precautions TEXT;

-- 新增主要成分欄位
ALTER TABLE drugs ADD COLUMN ingredient TEXT;

-- 新增藥品分類欄位
ALTER TABLE drugs ADD COLUMN category TEXT;

-- 新增製造商欄位
ALTER TABLE drugs ADD COLUMN manufacturer TEXT;

-- 新增儲存條件欄位
ALTER TABLE drugs ADD COLUMN storage_conditions TEXT;

-- 新增有效期限欄位
ALTER TABLE drugs ADD COLUMN expiry_info TEXT;
