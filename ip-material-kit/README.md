<!--
 * @Description: 
 * @Author: cct
 * @Date: 2026-09-01 11:38:56
 * @LastEditTime: 2026-09-01 11:38:59
 * @FilePath: /ip-material-kit/README.md
-->
# IP Material Kit

一个用于抓取、清洗和标准化 IP 道具资料的 Python 自动化脚本项目，适合用于生成漫画/图鉴类数据集。

当前支持的示例：
- 哆啦A梦道具图鉴

## 功能概览

- 按 IP 配置加载采集规则
- 支持按名称列表抓取或按漫画卷集抓取
- 批量下载原图
- 统一处理图片尺寸和质量
- 清洗数据字段
- 校验图片是否存在
- 输出最终 JSON 数据，供预览、Kindle 或其他页面使用

## 目录结构

```text
.
├── main.py                   # 主入口，启动抓取流程
├── auto_full_run.py          # 全自动流水线入口
├── run_image_proc.py         # 图片处理脚本
├── sync_json_img.py          # 同步 JSON 中的图片路径
├── validator.py              # 兼容性校验脚本
├── config/
│   ├── doraemon.json         # 哆啦A梦配置
│   └── pokemon.json          # 其他 IP 配置示例
├── modules/
│   ├── config_loader.py      # 配置读取
│   ├── crawler.py            # 按名称抓取器
│   ├── volume_crawler.py     # 按卷抓取器
│   ├── downloader.py         # 图片下载器
│   ├── image_processor.py    # 图片处理器
│   ├── data_cleaner.py       # 数据清洗器
│   ├── validator.py          # 校验器
│   └── ...
├── raw/
│   └── doraemon/
│       ├── html/
│       └── images_raw/
├── output/
│   └── doraemon/
│       ├── data.json
│       ├── data_valid.json
│       ├── data_missing.json
│       ├── images/
│       └── images_kindle/
└── README.md
```

## 环境准备

建议使用 Python 3.10+。

安装依赖：

```bash
pip install requests beautifulsoup4 pillow opencc
```

如果你已使用虚拟环境，也可以在项目根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4 pillow opencc
```

## 配置说明

配置文件位于 `config/` 下，格式为 JSON。每个 IP 都有一个对应的配置文件，例如：

- `config/doraemon.json`

典型字段说明：

```json
{
  "name": "哆啦A梦道具图鉴",
  "filename_prefix": "item-",
  "image_width": 650,
  "jpg_quality": 75,
  "crawler": {
    "mode": "volume",
    "volume_start": 1,
    "volume_end": 1,
    "deep_parse": true,
    "delay": 2,
    "convert_simple": true
  }
}
```

说明：
- `mode`：采集模式
  - `volume`：按漫画卷集抓取
  - `list`：按名称列表抓取
- `volume_start` / `volume_end`：抓取卷区间
- `deep_parse`：是否抓取详情页中的描述和图片

## 运行方式

### 1. 运行主流程

```bash
python3 main.py doraemon
```

说明：
- `doraemon` 是配置文件名对应的 IP 名称
- 程序会读取 `config/doraemon.json`
- 会下载图片、处理图片、清洗数据并输出 JSON

### 2. 只抓取指定卷

```bash
python3 main.py doraemon --vol 1
```

这会仅抓取第 1 卷。

### 3. 全自动流水线

```bash
python3 auto_full_run.py
```

该脚本会依次执行：
1. 图片批量处理
2. 同步 JSON 与图片路径
3. 校验图片有效性

### 4. 单独处理图片

```bash
python3 run_image_proc.py
```

### 5. 单独同步 JSON 图片路径

```bash
python3 sync_json_img.py
```

## 输出结果

抓取完成后，默认输出目录如下：

- `output/doraemon/data.json`：原始结果数据
- `output/doraemon/data_valid.json`：校验后有效数据
- `output/doraemon/data_missing.json`：缺失图片清单
- `output/doraemon/images/`：处理后标准图片
- `output/doraemon/images_kindle/`：适配 Kindle 的压缩图片

## 常见问题

### 1. `AttributeError: ... has no attribute ...`

通常是因为：
- 项目中接口变更后，调用代码还在用旧方法名
- 或配置/脚本版本未同步

解决方法：
- 确认你使用的是当前代码中的入口脚本
- 重新检查 `main.py` 和模块中的方法签名

### 2. 未找到配置文件

如果报错：

```text
FileNotFoundError: 未找到IP配置文件
```

请确认：
- `config/` 目录中存在对应的 JSON 文件
- 传入的 `ip_name` 与配置文件名一致

### 3. 图片下载失败

检查：
- 网络连接是否正常
- 目标网站是否对请求有限制
- `delay` 参数是否过低导致被拦截

## 备注

这是一个偏脚本型项目，而不是完整的 Web 应用。它更适合用于：
- 数据采集
- 图片标准化
- 图鉴/词典类内容生成
- 轻量级自动化流程

如果你想继续扩展项目，可以考虑添加：
- 统一的依赖文件 `requirements.txt`
- 更完整的日志输出
- 错误重试机制
- 多 IP 一键全量抓取

## 许可

该项目适用于本地研究与个人数据整理用途。若用于商业用途，请确认目标站点的使用政策和版权要求。
