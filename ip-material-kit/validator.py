'''
Description: 
Author: cct
Date: 2026-09-01 11:08:29
LastEditTime: 2026-09-01 11:08:31
FilePath: /ip-material-kit/import json.py
'''
import json
import os

def main():
    JSON_IN = "./output/doraemon/data.json"
    JSON_VALID = "./output/doraemon/data_valid.json"
    JSON_MISS = "./output/doraemon/data_missing.json"
    IMG_DIR = "./output/doraemon/images_kindle"

    if not os.path.exists(JSON_IN):
        print("data.json 不存在！")
        return

    with open(JSON_IN, "r", encoding="utf-8") as f:
        items = json.load(f)

    valid = []
    missing = []

    for item in items:
        img_path = item.get("img_filename", "")
        if not img_path:
            missing.append(item)
            continue

        img_file = os.path.basename(img_path)
        full_path = os.path.join(IMG_DIR, img_file)

        if os.path.exists(full_path):
            valid.append(item)
        else:
            missing.append(item)

    # 保存干净可用数据（预览/Kindle 只读这个）
    with open(JSON_VALID, "w", encoding="utf-8") as f:
        json.dump(valid, f, ensure_ascii=False, indent=2)

    # 保存缺失图片清单排查用
    with open(JSON_MISS, "w", encoding="utf-8") as f:
        json.dump(missing, f, ensure_ascii=False, indent=2)

    print(f"✅ 校验完成：有效 {len(valid)} 条 | 缺失 {len(missing)} 条")

if __name__ == "__main__":
    main()
