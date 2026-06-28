<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Whisper-faster--whisper-FF6B6B?style=flat" alt="Whisper">
  <img src="https://img.shields.io/badge/PDF-XeLaTeX-008080?style=flat&logo=latex&logoColor=white" alt="LaTeX">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=flat&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License">
</p>

<h1 align="center">🎙️ xiaoyuzhou-to-pdf</h1>

<p align="center">
  <b>小宇宙播客 → 美观 PDF 摘要，一条命令搞定</b>
</p>

<p align="center">
  自动下载音频 · 本地 Whisper 转录 · XeLaTeX 专业排版
</p>

<br>

## ✨ 效果预览

生成的 PDF 包含：

- 🎨 **深蓝主题封面** — 标题、嘉宾、时长信息卡片
- 📑 **六栏目录页** — 章节编号 + 标题 + 描述
- 📝 **正文排版** — 宋体正文 + 微软雅黑标题，1.5 倍行距
- 💬 **引用框** — 金句用圆角蓝灰底色框突出
- 🏷️ **金句合集** — 末页六条编号金句

> 效果参考：`output/summary.pdf`（运行后生成）

<br>

## 🚀 快速开始

### 依赖安装

```bash
# Python 依赖
pip install faster-whisper

# 系统工具（Windows）
# ffmpeg: https://ffmpeg.org/download.html
# MiKTeX: https://miktex.org/download
```

### 一键运行

```bash
# Step 1: 下载音频 + 本地转录
python scripts/transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxxxx" ./output

# Step 2: 生成 PDF
python scripts/summarize.py ./output
```

输出：
```
output/
├── transcript.txt    # 完整转录文本
├── meta.txt          # 元数据（标题、时长、字数）
├── summary.tex       # LaTeX 源文件（可二次修改）
└── summary.pdf       # 最终 PDF ✨
```

<br>

## 📋 工作流程

```
 小宇宙链接
    │
    ▼
┌─────────────────┐
│  ① curl 抓取页面  │  解析音频 URL + 标题
└────────┬────────┘
         ▼
┌─────────────────┐
│  ② 下载原始音频   │  m4a/mp3, 通常 ~100MB
└────────┬────────┘
         ▼
┌─────────────────┐
│  ③ ffmpeg 转码   │  64kbps 单声道 MP3, ~60MB
└────────┬────────┘
         ▼
┌─────────────────┐
│  ④ faster-whisper│  medium 模型, CPU 运行
│     本地转录      │  137 分钟 ≈ 30-60 分钟
└────────┬────────┘
         ▼
┌─────────────────┐
│  ⑤ 自动分段+排版  │  6 章节 + 6 金句提取
└────────┬────────┘
         ▼
┌─────────────────┐
│  ⑥ XeLaTeX 编译  │  封面 + 目录 + 正文 + 金句
└────────┬────────┘
         ▼
      PDF ✨
```

<br>

## 🛠️ 作为 Hermes Skill

对话中直接使用：

```
> 帮我总结这个播客 https://www.xiaoyuzhoufm.com/episode/xxxxx
```

Hermes 会自动加载 `SKILL.md` 并执行完整流水线。

<br>

## ⚙️ 命令参考

### transcribe.py

```bash
python scripts/transcribe.py <小宇宙URL> [输出目录]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| URL | 小宇宙播客链接 | 必填 |
| 输出目录 | 转录文件保存位置 | `./output` |

### summarize.py

```bash
python scripts/summarize.py <目录>
```

读取目录中的 `meta.txt` + `transcript.txt`，生成 `summary.pdf`。

<br>

## 📊 性能参考

| 播客时长 | 下载 | 转码 | 转录 (CPU) | PDF 编译 | 总计 |
|----------|------|------|-----------|----------|------|
| 30 分钟 | ~10s | ~5s | ~10-15 min | ~10s | ~15 min |
| 60 分钟 | ~20s | ~10s | ~20-30 min | ~15s | ~30 min |
| 137 分钟 | ~40s | ~20s | ~45-60 min | ~20s | ~60 min |

> 测试环境：Windows 11, Intel Core i7, 16GB RAM

<br>

## 🔧 故障排查

| 问题 | 解决方案 |
|------|----------|
| `faster-whisper` 未安装 | `pip install faster-whisper` |
| `xelatex` 未找到 | 安装 [MiKTeX](https://miktex.org/download) 并确保 PATH 包含 |
| 中文显示为方框 □ | 确认 `C:\Windows\Fonts\simsun.ttc` 和 `msyh.ttc` 存在 |
| 转录太慢 | 可升级到 `large-v3` 模型（更准但慢 3×）|
| `ffmpeg` 未找到 | 安装 ffmpeg 并加入 PATH |

<br>

## 📄 License

MIT © 2024
