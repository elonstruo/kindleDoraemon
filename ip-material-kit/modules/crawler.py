'''
Description: 
Author: cct
Date: 2026-08-28 16:05:09
LastEditTime: 2026-08-28 16:21:35
FilePath: /ip-material-kit/modules/crawler.py
'''
# 爬虫模块
import requests
from bs4 import BeautifulSoup
import time
from opencc import OpenCC

class DoraemonCrawler:
    def __init__(self, delay=2):
        self.delay = delay
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://chinesedora.com/"
        }
        self.base_url = "https://chinesedora.com"
        self.cc = OpenCC('t2s')  # 繁转简

    def _to_s(self, text):
        return self.cc.convert(text.strip()) if text else ""

    def search_item(self, keyword):
        """搜索道具，返回第一个匹配的详情页URL"""
        try:
            # WordPress 正确搜索参数：?s=
            search_url = f"{self.base_url}/?s={keyword}"
            resp = requests.get(search_url, headers=self.headers, timeout=10)
            resp.encoding = "utf-8"
            if resp.status_code != 200:
                return None

            soup = BeautifulSoup(resp.text, "html.parser")
            
            # 取第一个搜索结果链接
            first_link = soup.select_one("h2.entry-title a")
            if first_link:
                return first_link["href"]
            return None
        except Exception as e:
            print(f"  ✗ 搜索出错：{e}")
            return None

    def parse_detail(self, name, url):
        """解析道具详情页，提取信息和原图"""
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            resp.encoding = "utf-8"
            if resp.status_code != 200:
                print(f"  ✗ 页面请求失败，状态码 {resp.status_code}")
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            # 1. 提取主图
            main_img = soup.select_one(".entry-content img")
            image_url = ""
            if main_img and main_img.has_attr("src"):
                image_url = main_img["src"]
                if image_url.startswith("//"):
                    image_url = "https:" + image_url

            # 2. 提取正文段落
            paragraphs = soup.select(".entry-content p")
            desc = ""
            source = ""
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if not text:
                    continue
                # 第一段作为功能描述
                if not desc and len(text) > 10:
                    desc = text
                # 识别出处行
                if "漫画" in text and "话" in text:
                    source = text
                    break

            # 3. 全部转简体
            name = self._to_s(name)
            desc = self._to_s(desc)
            source = self._to_s(source)

            time.sleep(self.delay)
            return {
                "name": name,
                "desc": desc,
                "source": source,
                "image_url": image_url,
                "page_url": url
            }
        except Exception as e:
            print(f"  ✗ 解析异常：{e}")
            return None

    def batch_crawl(self, name_list):
        """批量爬取，输入名称列表"""
        results = []
        failed = []
        
        for i, name in enumerate(name_list):
            print(f"[{i+1}/{len(name_list)}] 正在采集：{name}")
            
            detail_url = self.search_item(name)
            if not detail_url:
                print(f"  ✗ 未找到对应页面")
                failed.append(name)
                continue

            data = self.parse_detail(name, detail_url)
            if not data:
                print(f"  ✗ 页面解析失败")
                failed.append(name)
                continue

            print(f"  ✓ 采集完成：{data['name']}")
            results.append(data)
        
        return results, failed
