namespace DrugManagementSystem
{
    partial class DrugEditForm
    {
        private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabBasic;
        private System.Windows.Forms.TabPage tabClinical;
        private System.Windows.Forms.TabPage tabOther;
        private System.Windows.Forms.TextBox txtLicenseNumber;
        private System.Windows.Forms.TextBox txtChineseName;
        private System.Windows.Forms.TextBox txtEnglishName;
        private System.Windows.Forms.TextBox txtShape;
        private System.Windows.Forms.TextBox txtSpecialDosageForm;
        private System.Windows.Forms.TextBox txtColor;
        private System.Windows.Forms.TextBox txtSpecialOdor;
        private System.Windows.Forms.TextBox txtMark;
        private System.Windows.Forms.TextBox txtSize;
        private System.Windows.Forms.TextBox txtLabelFront;
        private System.Windows.Forms.TextBox txtLabelBack;
        private System.Windows.Forms.TextBox txtIndications;
        private System.Windows.Forms.TextBox txtDosage;
        private System.Windows.Forms.TextBox txtSideEffects;
        private System.Windows.Forms.TextBox txtContraindications;
        private System.Windows.Forms.TextBox txtPrecautions;
        private System.Windows.Forms.TextBox txtIngredient;
        private System.Windows.Forms.TextBox txtCategory;
        private System.Windows.Forms.TextBox txtManufacturer;
        private System.Windows.Forms.TextBox txtStorageConditions;
        private System.Windows.Forms.TextBox txtExpiryInfo;
        private System.Windows.Forms.Button btnSave;
        private System.Windows.Forms.Button btnCancel;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabBasic = new System.Windows.Forms.TabPage();
            this.tabClinical = new System.Windows.Forms.TabPage();
            this.tabOther = new System.Windows.Forms.TabPage();
            this.txtLicenseNumber = new System.Windows.Forms.TextBox();
            this.txtChineseName = new System.Windows.Forms.TextBox();
            this.txtEnglishName = new System.Windows.Forms.TextBox();
            this.txtShape = new System.Windows.Forms.TextBox();
            this.txtSpecialDosageForm = new System.Windows.Forms.TextBox();
            this.txtColor = new System.Windows.Forms.TextBox();
            this.txtSpecialOdor = new System.Windows.Forms.TextBox();
            this.txtMark = new System.Windows.Forms.TextBox();
            this.txtSize = new System.Windows.Forms.TextBox();
            this.txtLabelFront = new System.Windows.Forms.TextBox();
            this.txtLabelBack = new System.Windows.Forms.TextBox();
            this.txtIndications = new System.Windows.Forms.TextBox();
            this.txtDosage = new System.Windows.Forms.TextBox();
            this.txtSideEffects = new System.Windows.Forms.TextBox();
            this.txtContraindications = new System.Windows.Forms.TextBox();
            this.txtPrecautions = new System.Windows.Forms.TextBox();
            this.txtIngredient = new System.Windows.Forms.TextBox();
            this.txtCategory = new System.Windows.Forms.TextBox();
            this.txtManufacturer = new System.Windows.Forms.TextBox();
            this.txtStorageConditions = new System.Windows.Forms.TextBox();
            this.txtExpiryInfo = new System.Windows.Forms.TextBox();
            this.btnSave = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();

            this.tabControl1.SuspendLayout();
            this.SuspendLayout();

            // tabControl1
            this.tabControl1.Controls.Add(this.tabBasic);
            this.tabControl1.Controls.Add(this.tabClinical);
            this.tabControl1.Controls.Add(this.tabOther);
            this.tabControl1.Location = new System.Drawing.Point(12, 12);
            this.tabControl1.Size = new System.Drawing.Size(660, 520);
            this.tabControl1.SelectedIndex = 0;

            // tabBasic
            this.tabBasic.Text = "基本資訊";
            this.tabBasic.UseVisualStyleBackColor = true;
            this.tabBasic.AutoScroll = true;
            
            // Add controls to tabBasic with proper layout
            int yPos = 20;
            int labelX = 20;
            int textX = 140;
            int lineHeight = 40;
            
            this.tabBasic.Controls.Add(CreateLabel("*許可證字號：", labelX, yPos));
            this.txtLicenseNumber.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtLicenseNumber.Size = new System.Drawing.Size(480, 27);
            this.tabBasic.Controls.Add(this.txtLicenseNumber);
            yPos += lineHeight;
            
            this.tabBasic.Controls.Add(CreateLabel("*中文品名：", labelX, yPos));
            this.txtChineseName.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtChineseName.Size = new System.Drawing.Size(480, 27);
            this.tabBasic.Controls.Add(this.txtChineseName);
            yPos += lineHeight;
            
            this.tabBasic.Controls.Add(CreateLabel("英文品名：", labelX, yPos));
            this.txtEnglishName.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtEnglishName.Size = new System.Drawing.Size(480, 27);
            this.tabBasic.Controls.Add(this.txtEnglishName);
            yPos += lineHeight;
            
            this.tabBasic.Controls.Add(CreateLabel("形狀：", labelX, yPos));
            this.txtShape.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtShape.Size = new System.Drawing.Size(200, 27);
            this.tabBasic.Controls.Add(this.txtShape);
            
            this.tabBasic.Controls.Add(CreateLabel("特殊劑型：", 360, yPos));
            this.txtSpecialDosageForm.Location = new System.Drawing.Point(460, yPos - 3);
            this.txtSpecialDosageForm.Size = new System.Drawing.Size(160, 27);
            this.tabBasic.Controls.Add(this.txtSpecialDosageForm);
            yPos += lineHeight;
            
            this.tabBasic.Controls.Add(CreateLabel("顏色：", labelX, yPos));
            this.txtColor.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtColor.Size = new System.Drawing.Size(200, 27);
            this.tabBasic.Controls.Add(this.txtColor);
            
            this.tabBasic.Controls.Add(CreateLabel("特殊氣味：", 360, yPos));
            this.txtSpecialOdor.Location = new System.Drawing.Point(460, yPos - 3);
            this.txtSpecialOdor.Size = new System.Drawing.Size(160, 27);
            this.tabBasic.Controls.Add(this.txtSpecialOdor);
            yPos += lineHeight;
            
            this.tabBasic.Controls.Add(CreateLabel("刻痕：", labelX, yPos));
            this.txtMark.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtMark.Size = new System.Drawing.Size(480, 27);
            this.tabBasic.Controls.Add(this.txtMark);
            yPos += lineHeight;
            
            this.tabBasic.Controls.Add(CreateLabel("外觀尺寸：", labelX, yPos));
            this.txtSize.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtSize.Size = new System.Drawing.Size(480, 27);
            this.tabBasic.Controls.Add(this.txtSize);
            yPos += lineHeight;
            
            this.tabBasic.Controls.Add(CreateLabel("標註一：", labelX, yPos));
            this.txtLabelFront.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtLabelFront.Size = new System.Drawing.Size(480, 27);
            this.tabBasic.Controls.Add(this.txtLabelFront);
            yPos += lineHeight;
            
            this.tabBasic.Controls.Add(CreateLabel("標註二：", labelX, yPos));
            this.txtLabelBack.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtLabelBack.Size = new System.Drawing.Size(480, 27);
            this.tabBasic.Controls.Add(this.txtLabelBack);

            // tabClinical
            this.tabClinical.Text = "臨床資訊";
            this.tabClinical.UseVisualStyleBackColor = true;
            this.tabClinical.AutoScroll = true;
            
            yPos = 20;
            this.tabClinical.Controls.Add(CreateLabel("適應症：", labelX, yPos));
            yPos += 25;
            this.txtIndications.Location = new System.Drawing.Point(labelX, yPos);
            this.txtIndications.Multiline = true;
            this.txtIndications.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtIndications.Size = new System.Drawing.Size(600, 60);
            this.tabClinical.Controls.Add(this.txtIndications);
            yPos += 75;
            
            this.tabClinical.Controls.Add(CreateLabel("用法用量：", labelX, yPos));
            yPos += 25;
            this.txtDosage.Location = new System.Drawing.Point(labelX, yPos);
            this.txtDosage.Multiline = true;
            this.txtDosage.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtDosage.Size = new System.Drawing.Size(600, 60);
            this.tabClinical.Controls.Add(this.txtDosage);
            yPos += 75;
            
            this.tabClinical.Controls.Add(CreateLabel("副作用：", labelX, yPos));
            yPos += 25;
            this.txtSideEffects.Location = new System.Drawing.Point(labelX, yPos);
            this.txtSideEffects.Multiline = true;
            this.txtSideEffects.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtSideEffects.Size = new System.Drawing.Size(600, 60);
            this.tabClinical.Controls.Add(this.txtSideEffects);
            yPos += 75;
            
            this.tabClinical.Controls.Add(CreateLabel("禁忌症：", labelX, yPos));
            yPos += 25;
            this.txtContraindications.Location = new System.Drawing.Point(labelX, yPos);
            this.txtContraindications.Multiline = true;
            this.txtContraindications.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtContraindications.Size = new System.Drawing.Size(600, 60);
            this.tabClinical.Controls.Add(this.txtContraindications);
            yPos += 75;
            
            this.tabClinical.Controls.Add(CreateLabel("注意事項：", labelX, yPos));
            yPos += 25;
            this.txtPrecautions.Location = new System.Drawing.Point(labelX, yPos);
            this.txtPrecautions.Multiline = true;
            this.txtPrecautions.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtPrecautions.Size = new System.Drawing.Size(600, 60);
            this.tabClinical.Controls.Add(this.txtPrecautions);

            // tabOther
            this.tabOther.Text = "其他資訊";
            this.tabOther.UseVisualStyleBackColor = true;
            this.tabOther.AutoScroll = true;
            
            yPos = 20;
            this.tabOther.Controls.Add(CreateLabel("主要成分：", labelX, yPos));
            this.txtIngredient.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtIngredient.Size = new System.Drawing.Size(480, 27);
            this.tabOther.Controls.Add(this.txtIngredient);
            yPos += lineHeight;
            
            this.tabOther.Controls.Add(CreateLabel("藥品分類：", labelX, yPos));
            this.txtCategory.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtCategory.Size = new System.Drawing.Size(480, 27);
            this.tabOther.Controls.Add(this.txtCategory);
            yPos += lineHeight;
            
            this.tabOther.Controls.Add(CreateLabel("製造商：", labelX, yPos));
            this.txtManufacturer.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtManufacturer.Size = new System.Drawing.Size(480, 27);
            this.tabOther.Controls.Add(this.txtManufacturer);
            yPos += lineHeight;
            
            this.tabOther.Controls.Add(CreateLabel("儲存條件：", labelX, yPos));
            yPos += 25;
            this.txtStorageConditions.Location = new System.Drawing.Point(textX, yPos);
            this.txtStorageConditions.Multiline = true;
            this.txtStorageConditions.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtStorageConditions.Size = new System.Drawing.Size(480, 60);
            this.tabOther.Controls.Add(this.txtStorageConditions);
            yPos += 75;
            
            this.tabOther.Controls.Add(CreateLabel("有效期限：", labelX, yPos));
            this.txtExpiryInfo.Location = new System.Drawing.Point(textX, yPos - 3);
            this.txtExpiryInfo.Size = new System.Drawing.Size(480, 27);
            this.tabOther.Controls.Add(this.txtExpiryInfo);

            // btnSave
            this.btnSave.Location = new System.Drawing.Point(450, 545);
            this.btnSave.Size = new System.Drawing.Size(100, 35);
            this.btnSave.Text = "儲存";
            this.btnSave.Click += new System.EventHandler(this.btnSave_Click);

            // btnCancel
            this.btnCancel.Location = new System.Drawing.Point(560, 545);
            this.btnCancel.Size = new System.Drawing.Size(100, 35);
            this.btnCancel.Text = "取消";
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);

            // DrugEditForm
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 20F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(684, 591);
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnSave);
            this.Controls.Add(this.tabControl1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "藥物編輯";

            this.tabControl1.ResumeLayout(false);
            this.ResumeLayout(false);
        }

        private System.Windows.Forms.Label CreateLabel(string text, int x, int y)
        {
            var label = new System.Windows.Forms.Label();
            label.AutoSize = true;
            label.Location = new System.Drawing.Point(x, y);
            label.Text = text;
            return label;
        }
    }
}
