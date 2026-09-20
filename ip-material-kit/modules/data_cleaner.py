'''
Description: 
Author: cct
Date: 2026-08-28 15:58:57
LastEditTime: 2026-08-28 15:58:58
FilePath: /ip-material-kit/modules/data_cleaner.py
'''
# 数据清洗标准化
import re

class DataCleaner:
    def __init__(self, config):
        self.config = config

    def clean_item(self, item):
        """清洗单条数据：规范格式、精简字数、统一命名"""
        # 去除多余换行和空格
        for key in item:
            if isinstance(item[key], str):
                item[key] = re.sub(r'\s+', ' ', item[key]).strip()
        
        # 描述字数限制（适配Kindle单行显示）
        # if "desc" in item and len(item["desc"]) > 50:
        #     item["desc"] = item["desc"][:47] + "..."
        
        # 按配置补全默认字段
        if "default_fields" in self.config:
            for k, v in self.config["default_fields"].items():
                if k not in item or not item[k]:
                    item[k] = v
        
        return item

    def clean_list(self, items):
        return [self.clean_item(item) for item in items]
