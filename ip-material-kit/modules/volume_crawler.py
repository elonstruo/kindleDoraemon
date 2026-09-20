import requests
from bs4 import BeautifulSoup
import time
from opencc import OpenCC
import urllib.parse

SITE_BASE_URL = "https://chinesedora.com"

class VolumeCrawler:
    def __init__(self, delay=2, convert_simple=True):
        self.delay = delay
        self.convert_simple = convert_simple
        self.base_domain = SITE_BASE_URL
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": f"{self.base_domain}/gadget/category/doraemon/"
        }
        # 分页模板；page=1不带 /page/1，page>=2追加 /page/{page}
        self.url_pattern = f"{self.base_domain}/gadget/category/doraemon/doraemon-vol-{{}}"

        if convert_simple:
            self.cc = OpenCC('t2s')
    def get_volume_list(self):
        """自动获取全部短篇卷号 1~45"""
        # 哆啦A梦短篇单行本一共 1‑45卷
        return list(range(1,46))

    def _to_s(self, text):
        if not self.convert_simple or not text:
            return text.strip()
        return self.cc.convert(text.strip())

    def get_volume_base_url(self, vol_num):
        return self.url_pattern.format(vol_num)

    def _normalize_url(self, url):
        if not url:
            return ""
        if url.startswith("//"):
            return "https:" + url
        return urllib.parse.urljoin(self.base_domain, url)

    def parse_one_page(self, page_url):
        """解析单页，返回本页的道具列表"""
        resp = requests.get(page_url, headers=self.headers, timeout=15)
        resp.encoding = "utf-8"
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        main_content = soup.select_one("#main") or soup.select_one(".content") or soup.body
        page_items = []

        for a in main_content.find_all("a", href=True):
            name_raw = a.get_text(strip=True)
            href = self._normalize_url(a.get("href", ""))
            # 道具链接特征：包含「／」、链接以 /gadget/ 开头
            if ("／" in name_raw
                and "/gadget/" in href
                and len(name_raw) < 50):
                page_items.append({"name_raw": name_raw, "detail_url": href})
        return page_items

    def get_gadgets_in_volume(self, vol_num):
        """自动遍历该卷全部分页，合并 + 去重"""
        base_url = self.get_volume_base_url(vol_num)
        all_gadgets = []
        seen_urls = set()

        # 先拿第1页
        print(f"    读取分页：{base_url}")
        page1 = self.parse_one_page(base_url)
        for g in page1:
            if g["detail_url"] not in seen_urls:
                seen_urls.add(g["detail_url"])
                all_gadgets.append(g)

        # 尝试page2,page3,page4，遇到返回空列表就停止
        for page_idx in range(2,6):
            page_url = f"{base_url}/page/{page_idx}"
            print(f"    读取分页：{page_url}")
            page_list = self.parse_one_page(page_url)
            if len(page_list) == 0:
                print(f"    分页 {page_idx} 无数据，停止分页遍历")
                break
            for g in page_list:
                if g["detail_url"] not in seen_urls:
                    seen_urls.add(g["detail_url"])
                    all_gadgets.append(g)
            time.sleep(self.delay)
        return all_gadgets
    def parse_detail(self, detail_url):
        try:
            resp = requests.get(detail_url, headers=self.headers, timeout=15)
            resp.encoding = "utf-8"
            if resp.status_code != 200:
                return "", "", ""
            soup = BeautifulSoup(resp.text, "html.parser")
            content = soup.select_one(".entry-content")
            if content is None:
                content = soup.body

            # ========== 【修改图片抓取部分，替换原来一大段图片逻辑】 ==========
            main_img = ""
            # 精准定位：div.lefttable -> div.tool98 -> img
            lefttable = soup.find("div", class_="lefttable")
            if lefttable:
                tool98 = lefttable.find("div", class_="tool98")
                if tool98:
                    img_tag = tool98.find("img")
                    if img_tag:
                        src = img_tag.get("data-src", "") or img_tag.get("src", "")
                        if src:
                            main_img = src
            # 处理 // 开头的协议相对地址，并补全站点域名
            main_img = self._normalize_url(main_img)


            # 识别网站默认占位图，包含关键字就置空
            placeholder_keywords = [
                "/images/01.jpg",
                "c96850.jpg"
            ]
            is_placeholder = any(k in main_img for k in placeholder_keywords)
            if is_placeholder:
                main_img = ""
            # ==============================================================

            paragraphs = content.find_all("p")
            desc, source = "", ""
            for p in paragraphs:
                text = p.get_text(strip=True)
                if not text:
                    continue
                if not desc and len(text) > 10:
                    desc = text
                if "漫画" in text and "话" in text:
                    source = text
                    break
            time.sleep(self.delay)
            return self._to_s(desc), self._to_s(source), main_img
        except Exception as e:
            print(f"    ✗ 详情解析失败：{e}")
            return "", "", ""



    def crawl_volume(self, vol_num, deep_parse=True):
        print(f"  正在读取第 {vol_num} 卷...")
        gadgets = self.get_gadgets_in_volume(vol_num)
        print(f"  去重后总共找到 {len(gadgets)} 个道具")

        results = []
        for i, g in enumerate(gadgets):
            # 取／前面作为台译名称
            name_tw = g["name_raw"].split("／")[0]
            name = self._to_s(name_tw)
            print(f"  [{i+1}/{len(gadgets)}] {name}")

            item = {
                "name": name,
                "page_url": g["detail_url"],
                "image_url": ""
            }

            if deep_parse:
                desc, source, main_img = self.parse_detail(g["detail_url"])
                item["desc"] = desc
                item["source"] = source
                item["image_url"] = main_img

            results.append(item)
            time.sleep(0.5)
        return results
