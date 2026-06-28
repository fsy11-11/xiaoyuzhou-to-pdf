---
name: xiaoyuzhou-to-pdf
description: 输入小宇宙播客链接，自动转录并生成美观的中文 PDF 摘要。本地 Whisper + XeLaTeX 排版。
triggers:
  - 小宇宙
  - 播客
  - PDF 摘要
  - 转文字
  - xiaoyuzhoufm.com/episode
---

# 小宇宙 → PDF 摘要

## 用法

### Hermes 对话触发

直接发小宇宙链接，说「转成 PDF 摘要」：

```
https://www.xiaoyuzhoufm.com/episode/xxxxx 帮我总结成 PDF
```

### 命令行

```bash
cd ~/.hermes/skills/media/xiaoyuzhou-to-pdf

# 完整流程
python3.12 scripts/transcribe.py "<URL>" ./output
python3.12 scripts/summarize.py ./output/transcript.txt ./output
```

## 前置检查

```bash
# 确认依赖
python3.12 -c "import faster_whisper; print('OK')"
ffmpeg -version > /dev/null 2>&1 && echo "ffmpeg OK"
xelatex --version > /dev/null 2>&1 && echo "xelatex OK"
```

## 已知限制

- 本地 Whisper medium 模型，137 分钟播客约需 30-60 分钟（CPU）
- 目前转录前 60-90 分钟内容
- 摘要为启发式分段，非 LLM 智能摘要
- XeLaTeX 编译需要 Windows 中文字体

## 故障排查

| 问题 | 解决 |
|------|------|
| faster-whisper 未安装 | `pip install faster-whisper` |
| xelatex 未找到 | 安装 MiKTeX 并确认 PATH |
| 中文字体缺失 | 确认 `C:\Windows\Fonts\simsun.ttc` 存在 |
| 转录太慢 | 升级 large-v3 或改用 Groq API |
