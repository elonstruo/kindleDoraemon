"""
Kindle图鉴全自动流水线
执行顺序：
1. 批量处理图片（灰度、白底、缩放、极限压缩120KB）
2. 自动同步JSON图片路径
3. 校验图片有效性，生成干净可用的data_valid.json
"""
from modules.image_processor import ImageProcessor
import subprocess
import os

def main():
    print("========== 开始全自动Kindle适配流水线 ==========\n")

    # 1. 执行图片批量处理（适配你本地类参数，仅传原生支持参数）
    print("[1/3] 正在批量处理图片（优化适配Kindle、极速压缩）...")
    processor = ImageProcessor(target_width=650, jpg_quality=85)
    INPUT_DIR = "./raw/doraemon/images_raw"
    OUTPUT_DIR = "./output/doraemon/images_kindle"
    processor.process_folder(INPUT_DIR, OUTPUT_DIR)

    # 2. 执行JSON图片路径同步
    print("\n[2/3] 正在自动同步JSON图片路径...")
    if os.path.exists("sync_json_img.py"):
        subprocess.run(["python3", "sync_json_img.py"])
    else:
        print("sync_json_img.py 不存在，跳过路径同步")

    # 3. 执行数据校验，生成可用数据
    print("\n[3/3] 正在校验图片有效性、过滤裂图数据...")
    if os.path.exists("validator.py"):
        subprocess.run(["python3", "validator.py"])
    else:
        print("validator.py 不存在，跳过数据校验")

    print("\n========== 全部流程执行完毕 ==========")
    print("✅ 输出成品：output/doraemon/data_valid.json + images_kindle优化图片")
    print("✅ 可直接打开preview.html预览、推送Kindle使用")

if __name__ == "__main__":
    main()
