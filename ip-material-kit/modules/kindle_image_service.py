'''
Description: 
Author: cct
Date: 2026-09-11 19:43:27
LastEditTime: 2026-09-11 19:43:29
FilePath: /ip-material-kit/modules/kindle_image_service.py
'''
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Union

from PIL import Image, ImageOps

PathLike = Union[str, os.PathLike[str]]


@dataclass
class KindleImageConfig:
    max_width: int = 750
    quality: int = 85
    gray_mode: bool = True
    white_bg: tuple[int, int, int] = (255, 255, 255)


class KindleImageService:
    """统一处理图片，输出适合 Kindle 水墨屏展示的 JPG 文件。"""

    def __init__(self, config: KindleImageConfig | None = None):
        self.config = config or KindleImageConfig()

    @staticmethod
    def _as_path(value: PathLike) -> Path:
        return Path(value).expanduser().resolve()

    def process_file(self, source_path: PathLike, output_path: PathLike) -> Path:
        src = self._as_path(source_path)
        dst = self._as_path(output_path)
        dst.parent.mkdir(parents=True, exist_ok=True)

        img = Image.open(src)
        img = ImageOps.exif_transpose(img)

        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", img.size, self.config.white_bg)
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode == "RGBA":
                bg.paste(img, mask=img.split()[3])
            else:
                bg.paste(img)
            img = bg

        if self.config.gray_mode:
            img = img.convert("L")

        width, height = img.size
        if width > self.config.max_width:
            scale = self.config.max_width / width
            new_width = max(1, int(width * scale))
            new_height = max(1, int(height * scale))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 先写入目标文件，后续可在外部直接使用
        img.save(dst, "JPEG", quality=self.config.quality, optimize=True)
        return dst

    def process_directory(self, input_dir: PathLike, output_dir: PathLike) -> int:
        src_dir = self._as_path(input_dir)
        dst_dir = self._as_path(output_dir)
        dst_dir.mkdir(parents=True, exist_ok=True)

        if not src_dir.exists():
            print(f"⚠️ 原始图片目录不存在：{src_dir}")
            return 0

        success_count = 0
        for file_name in sorted(os.listdir(src_dir)):
            ext = file_name.lower()
            if not ext.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
                continue

            source_file = src_dir / file_name
            target_file = dst_dir / f"{Path(file_name).stem}.jpg"
            try:
                self.process_file(source_file, target_file)
                success_count += 1
            except Exception as exc:  # pragma: no cover - non-critical for CLI usage
                print(f"❌ 处理失败：{source_file} -> {exc}")

        print(f"\n✅ Kindle 图片批量处理完成！成功处理 {success_count} 张图片")
        return success_count
