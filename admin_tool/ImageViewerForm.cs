using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

namespace DrugManagementSystem
{
    public partial class ImageViewerForm : Form
    {
        private readonly List<string> imageFiles;
        private readonly string photoDirectory;
        private int currentIndex = 0;

        public ImageViewerForm(List<string> images, string photoDir, string drugName)
        {
            InitializeComponent();
            imageFiles = images;
            photoDirectory = photoDir;
            this.Text = $"查看圖片 - {drugName}";
            
            if (imageFiles.Count > 0)
            {
                ShowImage(0);
            }
            else
            {
                lblInfo.Text = "無圖片";
            }

            UpdateNavigationButtons();
        }

        private void ShowImage(int index)
        {
            if (index < 0 || index >= imageFiles.Count)
                return;

            currentIndex = index;
            string imagePath = Path.Combine(photoDirectory, imageFiles[index]);

            if (File.Exists(imagePath))
            {
                try
                {
                    // 釋放舊圖片
                    if (pictureBox1.Image != null)
                    {
                        pictureBox1.Image.Dispose();
                    }

                    // 載入新圖片
                    using (var fs = new FileStream(imagePath, FileMode.Open, FileAccess.Read))
                    {
                        pictureBox1.Image = Image.FromStream(fs);
                    }

                    lblInfo.Text = $"{currentIndex + 1} / {imageFiles.Count} - {imageFiles[index]}";
                }
                catch (Exception ex)
                {
                    lblInfo.Text = $"載入失敗：{ex.Message}";
                    pictureBox1.Image = null;
                }
            }
            else
            {
                lblInfo.Text = $"找不到檔案：{imageFiles[index]}";
                pictureBox1.Image = null;
            }

            UpdateNavigationButtons();
        }

        private void UpdateNavigationButtons()
        {
            btnPrevious.Enabled = currentIndex > 0;
            btnNext.Enabled = currentIndex < imageFiles.Count - 1;
        }

        private void btnPrevious_Click(object sender, EventArgs e)
        {
            ShowImage(currentIndex - 1);
        }

        private void btnNext_Click(object sender, EventArgs e)
        {
            ShowImage(currentIndex + 1);
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                if (pictureBox1.Image != null)
                {
                    pictureBox1.Image.Dispose();
                }
                if (components != null)
                {
                    components.Dispose();
                }
            }
            base.Dispose(disposing);
        }
    }
}
