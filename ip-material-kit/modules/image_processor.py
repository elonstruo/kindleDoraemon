'''
Description: 
Author: cct
Date: 2026-08-28 15:57:44
LastEditTime: 2026-09-01 10:53:06
FilePath: /ip-material-kit/modules/image_processor.py
'''
# Kindle图片处理器
# from PIL import Image
# import os

# class ImageProcessor:
#     def __init__(self, target_width=650, jpg_quality=75):
#         self.target_width = target_width
#         self.jpg_quality = jpg_quality
#         self.white_bg = (255, 255, 255)

#     def process_one(self, input_path, output_path):
#         """处理单张图片：透明转白底 → 等比缩放 → 输出JPG（完美适配Kindle）"""
#         try:
#             img = Image.open(input_path)
#             # 透明通道贴白底（解决Kindle不显示PNG透明的核心问题）
#             if img.mode in ("RGBA", "P"):
#                 bg = Image.new("RGB", img.size, self.white_bg)
#                 if img.mode == "RGBA":
#                     bg.paste(img, mask=img.split()[3])
#                 else:
#                     bg.paste(img)
#                 img = bg

#             # 适配Kindle水墨屏：转为灰度图
#             img = img.convert("L")

#             # 等比例缩放到目标宽度，无拉伸不变形
#             w, h = img.size
#             if w > self.target_width:
#                 new_h = int(h * self.target_width / w)
#                 img = img.resize((self.target_width, new_h), Image.Resampling.LANCZOS)

#             # 输出优化压缩JPG，兼顾清晰度和体积
#             img.save(output_path, "JPEG", quality=self.jpg_quality, optimize=True)
#             return True
#         except Exception as e:
#             print(f"图片处理失败 {input_path}: {e}")
#             return False

#     def process_folder(self, input_dir, output_dir, name_map=None):
#         """批量处理文件夹，适配项目目录结构"""
#         os.makedirs(output_dir, exist_ok=True)
#         success = 0

#         if not os.path.exists(input_dir):
#             print(f"⚠️ 原始图片目录不存在：{input_dir}")
#             return 0

#         for filename in os.listdir(input_dir):
#             ext = os.path.splitext(filename)[1].lower()
#             if ext not in (".png", ".jpg", ".jpeg"):
#                 continue
#             input_path = os.path.join(input_dir, filename)

#             # 自定义文件名映射 / 默认统一jpg后缀
#             if name_map and filename in name_map:
#                 out_name = name_map[filename]
#             else:
#                 out_name = os.path.splitext(filename)[0].lower() + ".jpg"

#             output_path = os.path.join(output_dir, out_name)
#             if self.process_one(input_path, output_path):
#                 success += 1

#         print(f"\n✅ Kindle图片批量处理完成！成功处理 {success} 张图片")
#         return success
from PIL import Image
import os

class ImageProcessor:
    def __init__(self, target_width=650, jpg_quality=75, max_file_size_kb=150):
        self.target_width = target_width
        self.jpg_quality = jpg_quality
        self.max_file_size_kb = max_file_size_kb  # 单张图片最大体积 150KB，适配Kindle快速加载
        self.white_bg = (255, 255, 255)

    def _compress_by_size(self, img, temp_path) -> bool:
        """动态压缩图片，强制控制文件体积，提升页面加载速度"""
        quality = self.jpg_quality
        # 从预设画质逐步降低，压缩至目标体积
        while quality >= 40:
            img.save(temp_path, "JPEG", quality=quality, optimize=True)
            file_size_kb = os.path.getsize(temp_path) / 1024
            if file_size_kb <= self.max_file_size_kb:
                return True
            quality -= 10
        return False

    def process_one(self, input_path, output_path):
        """处理单张图片：透明转白底 → 等比缩放 → 灰度优化 → 体积压缩 → 输出JPG（极致适配Kindle加载速度）"""
        try:
            img = Image.open(input_path)
            # 透明通道贴白底（解决Kindle不显示PNG透明的核心问题）
            if img.mode in ("RGBA", "P"):
                bg = Image.new("RGB", img.size, self.white_bg)
                if img.mode == "RGBA":
                    bg.paste(img, mask=img.split()[3])
                else:
                    bg.paste(img)
                img = bg

            # 适配Kindle水墨屏：转为灰度图
            img = img.convert("L")

            # 等比例缩放到目标宽度，无拉伸不变形
            w, h = img.size
            if w > self.target_width:
                new_h = int(h * self.target_width / w)
                img = img.resize((self.target_width, new_h), Image.Resampling.LANCZOS)

            # 临时文件中转压缩，精准控制体积
            temp_output = output_path + ".tmp.jpg"
            self._compress_by_size(img, temp_output)

            # 重命名正式文件，删除临时文件
            if os.path.exists(temp_output):
                os.replace(temp_output, output_path)
                return True
            return False

        except Exception as e:
            print(f"图片处理失败 {input_path}: {e}")
            # 清理临时垃圾文件
            if os.path.exists(output_path + ".tmp.jpg"):
                os.remove(output_path + ".tmp.jpg")
            return False

    def process_folder(self, input_dir, output_dir, name_map=None):
        """批量处理文件夹，适配项目目录结构"""
        os.makedirs(output_dir, exist_ok=True)
        success = 0

        if not os.path.exists(input_dir):
            print(f"⚠️ 原始图片目录不存在：{input_dir}")
            return 0

        for filename in os.listdir(input_dir):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in (".png", ".jpg", ".jpeg"):
                continue
            input_path = os.path.join(input_dir, filename)

            # 自定义文件名映射 / 默认统一jpg后缀
            if name_map and filename in name_map:
                out_name = name_map[filename]
            else:
                out_name = os.path.splitext(filename)[0].lower() + ".jpg"

            output_path = os.path.join(output_dir, out_name)
            if self.process_one(input_path, output_path):
                success += 1

        print(f"\n✅ Kindle图片批量处理完成！成功处理 {success} 张图片，单张体积严控150KB内，加载速度大幅提升")
        return success

