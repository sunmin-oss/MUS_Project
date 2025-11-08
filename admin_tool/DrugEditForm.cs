using System;
using System.Data;
using System.Linq;
using System.Windows.Forms;

namespace DrugManagementSystem
{
    public partial class DrugEditForm : Form
    {
        private readonly DrugDatabase database;
        private readonly int? drugId;

        // 新增模式
        public DrugEditForm(DrugDatabase db)
        {
            InitializeComponent();
            database = db;
            drugId = null;
            this.Text = "新增藥物";
        }

        // 編輯模式
        public DrugEditForm(DrugDatabase db, int id)
        {
            InitializeComponent();
            database = db;
            drugId = id;
            this.Text = "編輯藥物";
            LoadDrugData(id);
        }

        private void LoadDrugData(int id)
        {
            try
            {
                var data = database.GetAllDrugs();
                var row = data.Select($"id = {id}").FirstOrDefault();
                
                if (row != null)
                {
                    // 基本資訊
                    txtLicenseNumber.Text = row["許可證字號"]?.ToString() ?? "";
                    txtChineseName.Text = row["中文品名"]?.ToString() ?? "";
                    txtEnglishName.Text = row["英文品名"]?.ToString() ?? "";
                    txtShape.Text = row["形狀"]?.ToString() ?? "";
                    txtSpecialDosageForm.Text = row["特殊劑型"]?.ToString() ?? "";
                    txtColor.Text = row["顏色"]?.ToString() ?? "";
                    txtSpecialOdor.Text = row["特殊氣味"]?.ToString() ?? "";
                    txtMark.Text = row["刻痕"]?.ToString() ?? "";
                    txtSize.Text = row["外觀尺寸"]?.ToString() ?? "";
                    txtLabelFront.Text = row["標註一"]?.ToString() ?? "";
                    txtLabelBack.Text = row["標註二"]?.ToString() ?? "";
                    
                    // 臨床資訊
                    txtIndications.Text = row["適應症"]?.ToString() ?? "";
                    txtDosage.Text = row["用法用量"]?.ToString() ?? "";
                    txtSideEffects.Text = row["副作用"]?.ToString() ?? "";
                    txtContraindications.Text = row["禁忌症"]?.ToString() ?? "";
                    txtPrecautions.Text = row["注意事項"]?.ToString() ?? "";
                    
                    // 其他資訊
                    txtIngredient.Text = row["主要成分"]?.ToString() ?? "";
                    txtCategory.Text = row["藥品分類"]?.ToString() ?? "";
                    txtManufacturer.Text = row["製造商"]?.ToString() ?? "";
                    txtStorageConditions.Text = row["儲存條件"]?.ToString() ?? "";
                    txtExpiryInfo.Text = row["有效期限"]?.ToString() ?? "";
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"載入資料失敗：{ex.Message}", "錯誤", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnSave_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(txtLicenseNumber.Text))
            {
                MessageBox.Show("請輸入許可證字號", "驗證失敗", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                txtLicenseNumber.Focus();
                return;
            }

            if (string.IsNullOrWhiteSpace(txtChineseName.Text))
            {
                MessageBox.Show("請輸入中文品名", "驗證失敗", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                txtChineseName.Focus();
                return;
            }

            try
            {
                if (drugId == null)
                {
                    // 新增
                    database.InsertDrug(
                        txtLicenseNumber.Text.Trim(),
                        txtChineseName.Text.Trim(),
                        txtEnglishName.Text.Trim(),
                        txtShape.Text.Trim(),
                        txtSpecialDosageForm.Text.Trim(),
                        txtColor.Text.Trim(),
                        txtSpecialOdor.Text.Trim(),
                        txtMark.Text.Trim(),
                        txtSize.Text.Trim(),
                        txtLabelFront.Text.Trim(),
                        txtLabelBack.Text.Trim(),
                        txtIndications.Text.Trim(),
                        txtDosage.Text.Trim(),
                        txtSideEffects.Text.Trim(),
                        txtContraindications.Text.Trim(),
                        txtPrecautions.Text.Trim(),
                        txtIngredient.Text.Trim(),
                        txtCategory.Text.Trim(),
                        txtManufacturer.Text.Trim(),
                        txtStorageConditions.Text.Trim(),
                        txtExpiryInfo.Text.Trim()
                    );
                }
                else
                {
                    // 更新
                    database.UpdateDrug(
                        drugId.Value,
                        txtLicenseNumber.Text.Trim(),
                        txtChineseName.Text.Trim(),
                        txtEnglishName.Text.Trim(),
                        txtShape.Text.Trim(),
                        txtSpecialDosageForm.Text.Trim(),
                        txtColor.Text.Trim(),
                        txtSpecialOdor.Text.Trim(),
                        txtMark.Text.Trim(),
                        txtSize.Text.Trim(),
                        txtLabelFront.Text.Trim(),
                        txtLabelBack.Text.Trim(),
                        txtIndications.Text.Trim(),
                        txtDosage.Text.Trim(),
                        txtSideEffects.Text.Trim(),
                        txtContraindications.Text.Trim(),
                        txtPrecautions.Text.Trim(),
                        txtIngredient.Text.Trim(),
                        txtCategory.Text.Trim(),
                        txtManufacturer.Text.Trim(),
                        txtStorageConditions.Text.Trim(),
                        txtExpiryInfo.Text.Trim()
                    );
                }

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"儲存失敗：{ex.Message}", "錯誤", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Cancel;
            this.Close();
        }
    }
}
