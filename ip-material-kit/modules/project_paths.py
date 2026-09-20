from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """集中管理单个 IP 的输入、输出和中间文件路径。"""

    root: Path
    ip_name: str

    @property
    def raw_dir(self) -> Path:
        return self.root / "raw" / self.ip_name

    @property
    def raw_images_dir(self) -> Path:
        return self.raw_dir / "images_raw"

    @property
    def raw_html_dir(self) -> Path:
        return self.raw_dir / "html"

    @property
    def output_dir(self) -> Path:
        return self.root / "output" / self.ip_name

    @property
    def processed_images_dir(self) -> Path:
        return self.output_dir / "images"

    @property
    def kindle_images_dir(self) -> Path:
        return self.output_dir / "images_kindle"

    @property
    def data_json(self) -> Path:
        return self.output_dir / "data.json"

    @property
    def valid_json(self) -> Path:
        return self.output_dir / "data_valid.json"

    @property
    def missing_json(self) -> Path:
        return self.output_dir / "data_missing.json"

    def ensure_dirs(self) -> None:
        for path in (self.raw_images_dir, self.raw_html_dir, self.output_dir,
                     self.processed_images_dir, self.kindle_images_dir):
            path.mkdir(parents=True, exist_ok=True)
