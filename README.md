# 小宇宙 → PDF 摘要

一条命令：输入小宇宙播客链接 → 本地 Whisper 转录 → 生成美观的中文 PDF 摘要。

## 快速开始

```bash
# 1. 安装依赖
pip install faster-whisper
# 确保已安装: ffmpeg, XeLaTeX (MiKTeX)

# 2. 转录
python scripts/transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxxxx" ./output

# 3. 生成 PDF
python scripts/summarize.py ./output/transcript.txt ./output
```

## 输出

```
output/
├── transcript.txt    # 完整转录文本
├── meta.txt          # 元数据（标题、时长、字数）
└── summary.pdf       # 排版好的 PDF 摘要
```

## 依赖

| 工具 | 用途 |
|------|------|
| Python 3.12+ | 运行环境 |
| faster-whisper | 本地语音转录 |
| ffmpeg / ffprobe | 音频下载和转码 |
| XeLaTeX (MiKTeX) | PDF 排版 |
| 中文字体 | simsun.ttc, msyh.ttc（Windows 自带） |

## 作为 Hermes Skill

将此目录放到 `~/.hermes/skills/media/xiaoyuzhou-to-pdf/`，然后对话中直接发小宇宙链接即可触发。

## License

MIT
