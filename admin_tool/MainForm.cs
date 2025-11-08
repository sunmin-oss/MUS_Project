using System;
using System.Data;
using System.IO;
using System.Windows.Forms;

namespace DrugManagementSystem
{
    public partial class MainForm : Form
    {
        private readonly DrugDatabase database = null!;
        private readonly string photoDirectory;

        public MainForm()
        {
            InitializeComponent();
            
            // 資料庫路徑：從專案根目錄回推
            string projectRoot = Path.Combine(Application.StartupPath, "..", "..", "..", "..");
            string dbPath = Path.GetFullPath(Path.Combine(projectRoot, "drug_recognition.db"));
            photoDirectory = Path.GetFullPath(Path.Combine(projectRoot, "medicine_photos"));

            if (!File.Exists(dbPath))
            {
                MessageBox.Show($"找不到資料庫檔案：{dbPath}", "錯誤", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Application.Exit();
                return;
            }

            database = new DrugDatabase(dbPath);
            LoadData();
            LoadFilters();
        }

        private void LoadData()
        {
            try
            {
                dataGridView1.DataSource = database.GetAllDrugs();
                // 隱藏 ID 欄位
                if (dataGridView1.Columns["id"] != null)
                {
                    dataGridView1.Columns["id"].Visible = false;
                }
                lblStatus.Text = $"共 {dataGridView1.Rows.Count} 筆資料";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"載入資料失敗：{ex.Message}", "錯誤", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void LoadFilters()
        {
            // 載入形狀選項
            cmbShape.Items.Clear();
            cmbShape.Items.AddRange(database.GetShapeOptions().ToArray());
            cmbShape.SelectedIndex = 0;

            // 載入顏色選項
            cmbColor.Items.Clear();
            cmbColor.Items.AddRange(database.GetColorOptions().ToArray());
            cmbColor.SelectedIndex = 0;

            // 載入月份選項
            cmbMonth.Items.Clear();
            cmbMonth.Items.Add("全部月份");
            for (int i = 1; i <= 12; i++)
            {
                cmbMonth.Items.Add(i.ToString("D2"));
            }
            cmbMonth.SelectedIndex = 0;
        }

        private void btnSearch_Click(object sender, EventArgs e)
        {
            try
            {
                string keyword = txtSearch.Text.Trim();
                string? shape = cmbShape.SelectedItem?.ToString();
                string? color = cmbColor.SelectedItem?.ToString();
                string? month = cmbMonth.SelectedItem?.ToString();

                dataGridView1.DataSource = database.SearchDrugs(keyword, shape, color, month);
                
                if (dataGridView1.Columns["id"] != null)
                {
                    dataGridView1.Columns["id"].Visible = false;
                }
                
                lblStatus.Text = $"找到 {dataGridView1.Rows.Count} 筆資料";
            }
            catch (Exception ex)
            {
                MessageBox.Show($"搜尋失敗：{ex.Message}", "錯誤", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnRefresh_Click(object sender, EventArgs e)
        {
            txtSearch.Clear();
            cmbShape.SelectedIndex = 0;
            cmbColor.SelectedIndex = 0;
            cmbMonth.SelectedIndex = 0;
            LoadData();
        }

        private void btnAdd_Click(object sender, EventArgs e)
        {
            using var form = new DrugEditForm(database);
            if (form.ShowDialog() == DialogResult.OK)
            {
                LoadData();
                MessageBox.Show("新增成功！", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void btnEdit_Click(object sender, EventArgs e)
        {
            if (dataGridView1.SelectedRows.Count == 0)
            {
                MessageBox.Show("請先選擇一筆資料", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            DataRowView row = (DataRowView)dataGridView1.SelectedRows[0].DataBoundItem;
            int id = Convert.ToInt32(row["id"]);

            using var form = new DrugEditForm(database, id);
            if (form.ShowDialog() == DialogResult.OK)
            {
                LoadData();
                MessageBox.Show("更新成功！", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void btnDelete_Click(object sender, EventArgs e)
        {
            if (dataGridView1.SelectedRows.Count == 0)
            {
                MessageBox.Show("請先選擇一筆資料", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            DataRowView row = (DataRowView)dataGridView1.SelectedRows[0].DataBoundItem;
            string chineseName = row["中文品名"]?.ToString() ?? "";

            var result = MessageBox.Show(
                $"確定要刪除「{chineseName}」嗎？\n此操作無法復原！",
                "確認刪除",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Warning
            );

            if (result == DialogResult.Yes)
            {
                try
                {
                    int id = Convert.ToInt32(row["id"]);
                    database.DeleteDrug(id);
                    LoadData();
                    MessageBox.Show("刪除成功！", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"刪除失敗：{ex.Message}", "錯誤", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        private void btnViewImages_Click(object sender, EventArgs e)
        {
            if (dataGridView1.SelectedRows.Count == 0)
            {
                MessageBox.Show("請先選擇一筆資料", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            DataRowView row = (DataRowView)dataGridView1.SelectedRows[0].DataBoundItem;
            int id = Convert.ToInt32(row["id"]);
            string chineseName = row["中文品名"]?.ToString() ?? "";

            var images = database.GetDrugImages(id);
            if (images.Count == 0)
            {
                MessageBox.Show("此藥物沒有圖片", "提示", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            using var form = new ImageViewerForm(images, photoDirectory, chineseName);
            form.ShowDialog();
        }

        private void txtSearch_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar == (char)Keys.Enter)
            {
                btnSearch_Click(sender, e);
                e.Handled = true;
            }
        }
    }
}
