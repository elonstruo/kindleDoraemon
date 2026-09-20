'''
Description: 
Author: cct
Date: 2026-08-28 15:57:00
LastEditTime: 2026-08-28 15:57:02
FilePath: /ip-material-kit/modules/config_loader.py
'''
# 配置加载器
import json
import os

class ConfigLoader:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir

    def load(self, ip_name):
        config_path = os.path.join(self.config_dir, f"{ip_name}.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"未找到IP配置文件：{config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
