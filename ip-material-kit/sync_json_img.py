'''
Description: 
Author: cct
Date: 2026-09-01 10:57:23
LastEditTime: 2026-09-01 14:26:52
FilePath: /ip-material-kit/sync_json_img.py
'''
# import json
# import os
# import re

# # 固定项目路径配置
# JSON_PATH = "./output/doraemon/data.json"
# KINDLE_IMG_DIR = "./output/doraemon/images_kindle"
# IMG_REL_PREFIX = "images_kindle/"

# def sync_img_path():
#     # 1. 精准读取并排序 item-001.jpg、item-002.jpg 序列图片
#     img_file_map = []
#     if os.path.exists(KINDLE_IMG_DIR):
#         for fname in os.listdir(KINDLE_IMG_DIR):
#             # 只匹配标准 item-三位序号.jpg 文件
#             if re.fullmatch(r"item-\d{3}\.jpg", fname.lower()):
#                 img_file_map.append(fname)
    
#     # 按序号从小到大排序，杜绝乱序
#     img_file_map.sort()

#     if not img_file_map:
#         print("❌ 未找到 item-001.jpg 序列图片！")
#         return

#     # 2. 读取原始JSON数据
#     with open(JSON_PATH, "r", encoding="utf-8") as f:
#         item_list = json.load(f)

#     total_valid = min(len(item_list), len(img_file_map))

#     # 3. 逐条绑定：第N条数据 = item-00N.jpg
#     for idx in range(len(item_list)):
#         if idx < total_valid:
#             item_list[idx]["img_filename"] = IMG_REL_PREFIX + img_file_map[idx]
#         else:
#             item_list[idx]["img_filename"] = ""

#     # 4. 写回修正数据
#     with open(JSON_PATH, "w", encoding="utf-8") as f:
#         json.dump(item_list, f, ensure_ascii=False, indent=2)

#     print("=" * 50)
#     print(f"✅ 序列图片路径同步完成")
#     print(f"✅ 成功绑定 {total_valid} 条 item-xxx.jpg 图片")
#     print(f"⚠️  剩余 {len(item_list)-total_valid} 条无匹配图片已清空")
#     print("=" * 50)

# if __name__ == "__main__":
#     sync_img_path()
import json
import os
import re

# 固定项目路径配置
JSON_PATH = "./output/doraemon/data.json"
KINDLE_IMG_DIR = "./output/doraemon/images_kindle"
IMG_REL_PREFIX = "images_kindle/"

def sync_img_path():
    # 1. 构建本地图片 序号-文件名 映射字典
    img_num_map = {}
    if os.path.exists(KINDLE_IMG_DIR):
        for fname in os.listdir(KINDLE_IMG_DIR):
            # 匹配 item-001.jpg / item-002.jpg 格式
            res = re.fullmatch(r"item-(\d{3})\.jpg", fname.lower())
            if res:
                num = res.group(1)
                img_num_map[num] = fname

    if not img_num_map:
        print("❌ 未找到 item-001.jpg 序列图片！")
        return

    # 2. 读取原始JSON数据
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        item_list = json.load(f)

    update_count = 0
    miss_count = 0

    # 3. 根据 no 字段精准匹配对应图片
    for item in item_list:
        no_str = item.get("no", "")
        # 提取 NO.001 中的三位数字
        res = re.search(r"(\d{3})", no_str)
        if not res:
            item["img_filename"] = ""
            miss_count += 1
            continue

        num_key = res.group(1)
        if num_key in img_num_map:
            # 精准对应：NO.001 → item-001.jpg
            item["img_filename"] = IMG_REL_PREFIX + img_num_map[num_key]
            update_count += 1
        else:
            item["img_filename"] = ""
            miss_count += 1

    # 4. 写回修正数据
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(item_list, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print(f"✅ 精准序号匹配同步完成")
    print(f"✅ 成功匹配绑定: {update_count} 条")
    print(f"⚠️  匹配失败/无图: {miss_count} 条")
    print("=" * 50)

if __name__ == "__main__":
    sync_img_path()


