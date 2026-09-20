'''
Description: 
Author: cct
Date: 2026-09-01 10:37:50
LastEditTime: 2026-09-01 10:54:09
FilePath: /ip-material-kit/run_image_proc.py
'''
# 项目根目录执行命令：python3 run_image_proc.py
from modules.image_processor import ImageProcessor

if __name__ == "__main__":
    # 初始化处理器：650宽度完美适配Kindle7
    processor = ImageProcessor(target_width=650, jpg_quality=75)

    # 固定项目路径
    INPUT_DIR = "./raw/doraemon/images_raw"
    OUTPUT_DIR = "./output/doraemon/images_kindle"

    # 批量处理（无需自定义文件名映射）
    processor.process_folder(INPUT_DIR, OUTPUT_DIR)
