import json
import re
from pathlib import Path


def sync_image_paths(json_path: str | Path, image_dir: str | Path,
                      image_prefix: str = "images_kindle/") -> tuple[int, int]:
    """按 NO.001 与 item-001.jpg 的序号同步 JSON 图片路径。"""
    json_path = Path(json_path)
    image_dir = Path(image_dir)
    image_map = {
        match.group(1): filename
        for filename in image_dir.iterdir()
        if filename.is_file()
        for match in [re.fullmatch(r"item-(\d{3})\.jpg", filename.name, re.IGNORECASE)]
        if match
    } if image_dir.exists() else {}

    with json_path.open("r", encoding="utf-8") as file:
        items = json.load(file)

    updated = 0
    missing = 0
    for item in items:
        match = re.search(r"(\d{3})", item.get("no", ""))
        filename = image_map.get(match.group(1)) if match else None
        item["img_filename"] = f"{image_prefix}{filename}" if filename else ""
        if filename:
            updated += 1
        else:
            missing += 1

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=2)
    return updated, missing
