#!/usr/bin/env python3
"""处理一张独立图片并输出到 Kindle 目录。"""

from __future__ import annotations

'''
Description: 
Author: cct
Date: 2026-09-11 19:43:48
LastEditTime: 2026-09-11 19:43:50
FilePath: /ip-material-kit/single_kindle_image.py
'''

import argparse
from pathlib import Path

from modules.kindle_image_service import KindleImageService


def main() -> int:
    parser = argparse.ArgumentParser(description="为 Kindle 生成单张图片")
    parser.add_argument("source", help="源图片路径，例如 ./raw/doraemon/images_raw/item-001.jpg")
    parser.add_argument(
        "--output",
        default="./output/doraemon/images_kindle/single_kindle_image.jpg",
        help="输出路径，默认写到 Kindle 图片目录下",
    )
    args = parser.parse_args()

    source_path = Path(args.source).expanduser()
    output_path = Path(args.output).expanduser()

    if not source_path.exists():
        raise FileNotFoundError(f"源图片不存在：{source_path}")

    service = KindleImageService()
    result = service.process_file(source_path, output_path)
    print(f"✅ 已生成 Kindle 图片：{result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
