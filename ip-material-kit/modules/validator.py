'''
Description: 
Author: cct
Date: 2026-08-28 15:59:53
LastEditTime: 2026-09-01 16:22:05
FilePath: /ip-material-kit/modules/validator.py
'''
# 质量校验器
import os
import json

class Validator:
    def __init__(self, image_base_dir: str):
        """
        :param image_base_dir: images_kindle 文件夹物理路径
        """
        self.image_base_dir = image_base_dir

    def validate(self, item_list: list[dict]) -> list[str]:
        """兼容旧调用：返回错误说明列表，保持 main.py 现有逻辑不变。"""
        errors = []
        for i, item in enumerate(item_list):
            for field in ["no", "name", "img_filename"]:
                if field not in item or not item.get(field):
                    errors.append(f"第{i+1}条缺少必填字段：{field}")

            img_rel = item.get("img_filename", "")
            if img_rel:
                fname = os.path.basename(img_rel)
                full_path = os.path.join(self.image_base_dir, fname)
                if not os.path.exists(full_path) or not os.path.isfile(full_path):
                    errors.append(f"第{i+1}条图片不存在：{img_rel}")

        return errors

    def check_single(self, item: dict) -> tuple[bool, str]:
        """校验单条道具的图片
        返回 (是否有效,提示信息)
        """
        img_rel = item.get("img_filename", "")
        if not img_rel:
            return False, "无图片字段"
        # 取文件名，去掉目录前缀
        fname = os.path.basename(img_rel)
        full_path = os.path.join(self.image_base_dir, fname)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return True, "ok"
        return False, f"文件缺失:{fname}"

    def validate_list(self, item_list: list[dict]) -> tuple[list[dict], list[dict]]:
        """
        :return: valid_items(图片正常), invalid_items(图片异常)
        """
        valid_items = []
        invalid_items = []
        for item in item_list:
            ok, msg = self.check_single(item)
            if ok:
                valid_items.append(item)
            else:
                item["_check_msg"] = msg
                invalid_items.append(item)
        return valid_items, invalid_items

    def run_and_save(self, json_in_path: str, json_out_valid: str, json_out_invalid: str):
        """
        读取原始data.json，输出：
        - valid：图片全部正常，给Kindle网页使用
        - invalid：图片缺失，用于排查补图
        """
        with open(json_in_path, "r", encoding="utf‑8") as f:
            items = json.load(f)

        valid, invalid = self.validate_list(items)

        with open(json_out_valid, "w", encoding="utf‑8") as f:
            json.dump(valid, f, ensure_ascii=False, indent=2)

        with open(json_out_invalid, "w", encoding="utf‑8") as f:
            json.dump(invalid, f, ensure_ascii=False, indent=2)

        print(f"校验完成：总 {len(items)} 条 | 有效 {len(valid)} 条 | 图片缺失 {len(invalid)} 条")
        for bad in invalid:
            print(f"  ⚠️ {bad.get('name','未知')} → {bad.get('_check_msg')}")
        return valid, invalid

