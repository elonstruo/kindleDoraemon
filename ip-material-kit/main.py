import os
import json
from modules.config_loader import ConfigLoader
from modules.crawler import DoraemonCrawler
from modules.volume_crawler import VolumeCrawler
from modules.downloader import ImageDownloader
from modules.image_processor import ImageProcessor
from modules.data_cleaner import DataCleaner
from modules.validator import Validator

def run(ip_name, list_file, single_vol=None):
    print(f"===== 开始处理 IP：{ip_name} =====")
    
    # 1. 加载配置
    config = ConfigLoader().load(ip_name)
    print(f"加载配置完成：{config['name']}")

    # 2. 目录初始化
    raw_img_dir = f"raw/{ip_name}/images_raw"
    output_img_dir = f"output/{ip_name}/images"
    output_json = f"output/{ip_name}/data.json"
    os.makedirs(raw_img_dir, exist_ok=True)
    os.makedirs(output_img_dir, exist_ok=True)

    # 3. 采集数据
    crawler_config = config.get("crawler", {})
    mode = crawler_config.get("mode", "list")
    raw_items = []
    failed = []

    if mode == "volume":
        print("\n--- 按漫画卷集模式采集 ---")
        vc = VolumeCrawler(
            delay=crawler_config.get("delay", 2),
            convert_simple=crawler_config.get("convert_simple", True)
        )
        
        # 获取所有卷列表
        print("正在获取卷集列表...")
        all_volume = vc.get_volume_list()
        if single_vol is not None:
            # 单卷模式：只抓取指定卷
            if single_vol not in all_volume:
                print(f"错误：卷号{single_vol}不在1‑45范围内")
                return
            volumes = [single_vol]
            print(f"===== 单卷模式，仅抓取第 {single_vol} 卷 =====")
        else:
            volumes = all_volume
            print(f"===== 全量模式，一共检测到 {len(volumes)} 个漫画卷 =====")

        # print(f"共找到 {len(volumes)} 卷")
        
        start = crawler_config.get("volume_start", 1) - 1
        end = crawler_config.get("volume_end", 1)
        target_volumes = volumes[start:end]
        
        for vol in target_volumes:
            print(f"\n== 正在抓取：第 {vol} 卷 ==")
            items = vc.crawl_volume(
                vol,
                deep_parse=crawler_config.get("deep_parse", True)
            )
            raw_items.extend(items)

    else:
        # 原有的按名称列表模式
        if not list_file:
            print("错误：列表模式需要指定列表文件")
            return
        
        print("\n--- 按名称列表模式采集 ---")
        with open(list_file, "r", encoding="utf-8") as f:
            names = [line.strip() for line in f if line.strip()]
        print(f"读取条目：{len(names)} 个")
        
        crawler = DoraemonCrawler(delay=crawler_config.get("delay", 2))
        raw_items, failed = crawler.batch_crawl(names)

    # 4. 补全编号、生成标准文件名
    print("\n--- 数据格式化 ---")
    items = []
    download_list = []
    for i, item in enumerate(raw_items):
        item["no"] = f"NO.{str(i+1).zfill(3)}"
        img_name = f"{config['filename_prefix']}{i+1:03d}.jpg"
        item["img_filename"] = img_name
        items.append(item)
        
        if item.get("image_url"):
            download_list.append((img_name, item["image_url"]))

    # 5. 批量下载原图
    print(f"\n--- 开始下载图片（共 {len(download_list)} 张）---")
    downloader = ImageDownloader(delay=1)
    dl_count = downloader.batch_download(download_list, raw_img_dir)
    print(f"下载完成：{dl_count} 张")

    # 6. 图片标准化处理
    print("\n--- 开始处理图片 ---")
    processor = ImageProcessor(
        target_width=config.get("image_width", 650),
        jpg_quality=config.get("jpg_quality", 75)
    )
    proc_count = processor.process_folder(raw_img_dir, output_img_dir)
    print(f"图片处理完成：{proc_count} 张")

    # 7. 数据清洗
    print("\n--- 数据清洗标准化 ---")
    items = DataCleaner(config).clean_list(items)

    # 8. 质量校验
    print("\n--- 质量校验 ---")
    errors = Validator(output_img_dir).validate(items)
    if errors:
        print("⚠️ 校验发现问题：")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ 校验全部通过")

    # 9. 输出最终JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"\n数据输出完成：{output_json}")
    
    if failed:
        print(f"\n⚠️ 采集失败 {len(failed)} 个：")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\n===== {ip_name} 处理完成 =====\n")

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip_name", help="IP名称 doraemon")
    parser.add_argument("--vol", type=int, default=None, help="指定单卷抓取，例如 --vol 1；不填抓取全部45卷")
    parser.add_argument("--list", default="volume", help="数据源配置文件")
    args = parser.parse_args()

    ip_name = args.ip_name
    list_file = args.list

    run(ip_name, list_file, single_vol=args.vol)

