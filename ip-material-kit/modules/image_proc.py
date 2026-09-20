'''
Description: 
Author: cct
Date: 2026-09-01 10:31:25
LastEditTime: 2026-09-01 10:31:27
FilePath: /ip-material-kit/modules/image_proc.py
'''
# 存放路径：modules/image_processor.py
# 供 main.py / 其他脚本导入调用，统一项目规范
import os
from PIL import Image

class KindleImageProcessor:
    # Kindle7 固定适配参数
    MAX_WIDTH = 750
    QUALITY = 85
    GRAY_MODE = True

    def process_one_image(self, in_path: str, out_path: str) -> bool:
        """处理单张图片：灰度转换、等比例缩放、统一JPG格式"""
        try:
            img = Image.open(in_path)

            # 兼容GIF格式，仅保留第一帧静态图
            if img.format == "GIF":
                img = img.convert("RGB")

            # 转换黑白灰度，适配Kindle水墨屏显示
            if self.GRAY_MODE:
                img = img.convert("L")

            # 等比例缩放，不拉伸、不变形
            w, h = img.size
            if w > self.MAX_WIDTH:
                scale = self.MAX_WIDTH / w
                new_w = int(w * scale)
                new_h = int(h * scale)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # 保存优化后图片
            img.save(out_path, "JPEG", quality=self.QUALITY)
            return True
        except Exception as e:
            print(f"❌ 图片处理失败：{os.path.basename(in_path)} - {str(e)}")
            return False

    def batch_process(self, input_dir: str, output_dir: str) -> int:
        """
        批量处理文件夹所有图片
        :param input_dir: 原始图片目录 raw_img
        :param output_dir: Kindle适配图输出目录
        :return: 成功处理图片数量
        """
        os.makedirs(output_dir, exist_ok=True)
        success_count = 0

        if not os.path.exists(input_dir):
            print(f"⚠️ 原始图片目录不存在：{input_dir}")
            return 0

        for fname in os.listdir(input_dir):
            ext = fname.lower()
            if not ext.endswith((".jpg", ".jpeg", ".png", ".gif")):
                continue

            in_file = os.path.join(input_dir, fname)
            base, _ = os.path.splitext(fname)
            out_file = os.path.join(output_dir, base + ".jpg")

            if self.process_one_image(in_file, out_file):
                success_count += 1

        print(f"\n✅ Kindle图片批量处理完成！成功处理 {success_count} 张图片")
        return success_count
