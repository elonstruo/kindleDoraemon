'''
Description: 
Author: cct
Date: 2026-08-28 15:58:07
LastEditTime: 2026-08-28 15:58:08
FilePath: /ip-material-kit/modules/downloader.py
'''
# 图片批量下载器
import requests
import os
import time

class ImageDownloader:
    def __init__(self, delay=1):
        self.delay = delay
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def download(self, url, save_path):
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(resp.content)
            time.sleep(self.delay)
            return True
        except Exception as e:
            print(f"下载失败 {url}: {e}")
            return False

    def batch_download(self, url_list, save_dir):
        """url_list格式：[(文件名, 网址), ...]"""
        success = 0
        for name, url in url_list:
            save_path = os.path.join(save_dir, name)
            if self.download(url, save_path):
                success += 1
        return success
