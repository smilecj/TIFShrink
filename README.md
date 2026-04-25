# TIFShrink Pro - 学术论文图片批量处理工具

## 项目概述

TIFShrink Pro 是一款专为学术研究者设计的图片批量处理工具，支持 TIFF、PNG、JPEG、PDF 等多种格式的转换和压缩。

**核心特点：**
- 支持**本地 Python 后端**进行真正的 TIFF 压缩
- 支持**浏览器原生**处理（无需安装任何软件）
- 支持**独立桌面应用**（双击即用）
- 100% 本地处理，数据不上传，保护隐私

## 三种使用方式

### 1. 独立桌面应用（推荐 - 最简单）

下载并运行 `TIFShrink.exe`，自动启动服务并打开浏览器界面。

**优势：**
- ✅ 双击即可运行，无需安装 Python 环境
- ✅ 自动检测端口占用
- ✅ 自动打开浏览器
- ✅ 支持真正的 TIFF LZW/Deflate 压缩

**使用方法：**
```bash
# 直接双击运行 build/tifshrink/TIFShrink.exe
# 或在命令行运行
./TIFShrink.exe
```

### 2. 本地服务模式

使用 Python 后端，支持**真正的 TIFF LZW/Deflate 压缩**。

**优势：**
- ✅ 支持 TIFF Deflate/LZW/PackBits/JPEG 压缩
- ✅ 可以显著减小 TIFF 文件体积
- ✅ 保持图片质量
- ✅ 所有处理在本地完成

**使用方法：**

```bash
# 1. 安装依赖
pip install Pillow Flask flask-cors

# 2. 启动本地服务
python server.py

# 3. 在浏览器打开 index.html
# 页面会自动检测到本地服务
```

**服务端口：** `http://127.0.0.1:18765`

### 3. 浏览器原生模式

无需安装任何软件，直接在浏览器中使用。

**限制：**
- ⚠️ TIFF 格式无法压缩（体积可能变大）
- ✅ PNG、JPEG、PDF 正常工作

## 功能说明

| 功能 | 桌面应用 | 本地服务 | 浏览器原生 |
|------|----------|----------|------------|
| TIFF Deflate 压缩 | ✅ | ✅ | ❌ |
| TIFF LZW 压缩 | ✅ | ✅ | ❌ |
| TIFF PackBits 压缩 | ✅ | ✅ | ❌ |
| TIFF JPEG 压缩 | ✅ | ✅ | ❌ |
| PNG 压缩 | ✅ | ✅ | ✅ |
| JPEG 压缩 | ✅ | ✅ | ✅ |
| PDF 生成 | ✅ | ✅ | ✅ |
| 批量处理 | ✅ | ✅ | ✅ |
| 隐私保护 | ✅ | ✅ | ✅ |

## TIFF 压缩算法说明

| 算法 | 说明 | 适用场景 |
|------|------|----------|
| **Deflate** | 最佳压缩率（推荐） | 体积优先，减小99% |
| **LZW** | 经典无损压缩，稳定可靠 | 通用场景 |
| **PackBits** | 快速压缩，适合连续色调 | 黑白图、快速处理 |
| **JPEG** | TIFF内嵌JPEG，有损压缩 | 最小体积 |
| **无压缩** | 保持原始数据 | 需要保持完全无损 |

## 输出格式对比

| 格式 | 压缩效果 | 适用场景 |
|------|----------|----------|
| **JPEG** | ✅ 显著减小 | 体积优先，减小文件大小 |
| **PNG** | ✅ 适中 | 无损压缩，支持透明 |
| **TIFF** | ✅ 本地服务可压缩 | 学术投稿，保持高质量 |
| **PDF** | ✅ 适中 | 出版标准，便于分享 |

## 技术栈

### 前端
- HTML/CSS/JavaScript
- [tiff.js](https://github.com/seikichi/tiff.js) - TIFF 编解码
- [canvas-to-tiff](https://github.com/motiz88/canvas-to-tiff) - Canvas 转 TIFF
- [jsPDF](https://github.com/MrRio/jsPDF) - PDF 生成
- [JSZip](https://github.com/Stuk/jszip) - ZIP 打包
- [Font Awesome](https://fontawesome.com) - 图标库

### 后端（本地服务）
- Python 3
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Flask-CORS](https://flask-cors.readthedocs.io/) - 跨域支持
- [Pillow](https://python-pillow.org/) - 图片处理

### 打包
- [PyInstaller](https://pyinstaller.org/) - 生成独立可执行文件

## 隐私说明

- 所有图片处理在本地完成
- 不上传到任何服务器
- 关闭浏览器/停止服务后数据自动清除

## 使用说明

### 方式一：独立桌面应用（最简单）

```bash
# 直接双击 build/tifshrink/TIFShrink.exe 运行
# 或在终端运行
./TIFShrink.exe

# 程序会自动：
# 1. 启动本地服务（端口 18765）
# 2. 打开默认浏览器
# 3. 关闭窗口即可退出程序
```

### 方式二：本地运行（完整功能）

```bash
# 克隆或下载项目

# 安装 Python 依赖
pip install Pillow Flask flask-cors

# 启动后端服务
python server.py

# 打开 index.html（可以放在任何地方，用浏览器打开即可）
# 或者用静态服务器
python -m http.server 8080
# 然后访问 http://localhost:8080
```

### 方式三：纯浏览器运行

直接用浏览器打开 `index.html` 即可使用基础功能（TIFF 压缩除外）。

## API 接口

本地服务提供以下 API：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/algorithms` | GET | 获取支持的压缩算法列表 |
| `/api/info` | POST | 获取图片信息 |
| `/api/compress` | POST | 压缩单张图片 |
| `/api/download/<token>` | GET | 下载处理后的文件 |
| `/api/batch` | POST | 批量处理 |
| `/api/batch-download/<token>` | GET | 下载批量处理的 ZIP |
| `/api/cleanup` | POST | 清理临时文件 |

### API 详情

#### `POST /api/compress`

压缩单张图片。

**参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| file | File | 图片文件 |
| format | string | 输出格式：tiff, png, jpeg, pdf |
| compression | string | TIFF压缩方式：deflate, lzw, packbits, jpeg, none |
| quality | int | 质量参数 (10-100) |

**响应：**
```json
{
  "success": true,
  "download_token": "xxx.tiff",
  "algorithm": "deflate",
  "original_size": 1048576,
  "compressed_size": 10240,
  "saved_percent": 99.02
}
```

## 更新日志

### v3.0.1 - 2026.04.25
- **新增独立桌面应用**：TIFShrink.exe 双击即用
- **新增 PackBits 压缩算法**：适合黑白图和快速处理
- **修正端口配置**：统一使用端口 18765
- **更新依赖说明**：新增 flask-cors

### v3.0 - 2026.04.19
- **新增本地 Python 后端**：支持真正的 TIFF LZW/Deflate 压缩
- **新增服务选择**：可切换本地服务/浏览器原生模式
- **智能自动检测**：页面自动检测本地服务是否运行
- **保持隐私**：所有处理仍在本地完成

### v2.3 - 2026.04.19
- 新增智能保护机制
- 新增处理确认对话框
- 优化统计显示

### v2.2 - 2026.04.19
- 修复格式选择问题
- 优化 TIFF 解码
- 新增缩放功能
- 新增键盘快捷键

## 常见问题

### Q: 如何让 TIFF 文件体积变小？

A: 有三种方式：
1. **最简单**：直接双击运行 `TIFShrink.exe`
2. 启动本地 Python 服务（`python server.py`），然后选择"本地服务"模式
3. 系统会使用 Deflate 压缩，可显著减小体积

### Q: 独立桌面应用安全吗？

A: 完全安全。所有处理都在你自己的电脑上完成，图片不会上传到任何服务器。

### Q: 为什么有浏览器原生模式？

A: 为了无需安装任何软件也能使用。如果只是转换 PNG/JPEG，不需要本地服务。

### Q: 各种压缩算法有什么区别？

| 算法 | 压缩速度 | 压缩率 | 画质保持 |
|------|----------|--------|----------|
| Deflate | 中等 | 最高 | 无损 |
| LZW | 中等 | 高 | 无损 |
| PackBits | 快 | 中等 | 无损 |
| JPEG | 快 | 最高 | 有损 |

### Q: 如何处理 RGBA 或透明背景图片？

A: 程序会自动将透明背景转换为白色背景，确保最大兼容性。

## 文件结构

```
TIFShrink-v3.0/
├── index.html          # 前端界面
├── main.py             # 桌面应用入口（PyInstaller）
├── server.py           # Flask 后端服务
├── README.md           # 本文档
├── build/
│   └── tifshrink/
│       └── TIFShrink.exe  # 独立可执行文件
└── tifshrink.spec      # PyInstaller 配置
```

## 版权声明

本项目仅供学习和非商业用途。使用的开源库均遵循 MIT 协议，版权归其各自作者所有。
