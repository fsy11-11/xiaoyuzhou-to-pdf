<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Whisper-faster--whisper-FF6B6B?style=flat" alt="Whisper">
  <img src="https://img.shields.io/badge/PDF-XeLaTeX-008080?style=flat&logo=latex&logoColor=white" alt="LaTeX">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=flat&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License">
</p>

<h1 align="center">🎙️ xiaoyuzhou-to-pdf</h1>

<p align="center">
  <b>Turn Xiaoyuzhou podcast episodes into beautiful PDF summaries — one command.</b>
</p>

<p align="center">
  Download · Transcribe (local Whisper) · Typeset (XeLaTeX)
</p>

<br>

## ✨ What You Get

The generated PDF features:

- 🎨 **Dark-blue themed cover** — title, guest, duration info card
- 📑 **Table of contents** — numbered chapters with descriptions
- 📝 **Professional typesetting** — SimSun body + Microsoft YaHei headings
- 💬 **Styled quote boxes** — key quotes in rounded blue-gray frames
- 🏷️ **Golden quotes page** — six numbered highlight quotes

> See: `output/summary.pdf` (generated after running)

<br>

## 🚀 Quick Start

### Prerequisites

```bash
# Python dependency
pip install faster-whisper

# System tools (Windows)
# ffmpeg: https://ffmpeg.org/download.html
# MiKTeX: https://miktex.org/download
```

### Run

```bash
# Step 1: Download + transcribe
python scripts/transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxxxx" ./output

# Step 2: Generate PDF
python scripts/summarize.py ./output
```

Output:
```
output/
├── transcript.txt    # Full transcription
├── meta.txt          # Metadata (title, duration, word count)
├── summary.tex       # LaTeX source (editable)
└── summary.pdf       # Final PDF ✨
```

<br>

## 📋 Pipeline

```
 Xiaoyuzhou URL
    │
    ▼
┌─────────────────┐
│  ① curl fetch     │  Extract audio URL + title
└────────┬────────┘
         ▼
┌─────────────────┐
│  ② Download audio │  m4a/mp3, ~100MB typical
└────────┬────────┘
         ▼
┌─────────────────┐
│  ③ ffmpeg encode  │  64kbps mono MP3, ~60MB
└────────┬────────┘
         ▼
┌─────────────────┐
│  ④ faster-whisper │  medium model, CPU-only
│     transcribe     │  137 min ≈ 30-60 min
└────────┬────────┘
         ▼
┌─────────────────┐
│  ⑤ Section + quote │  6 chapters + 6 quotes
│     extraction     │
└────────┬────────┘
         ▼
┌─────────────────┐
│  ⑥ XeLaTeX compile│  Cover + TOC + Body + Quotes
└────────┬────────┘
         ▼
      PDF ✨
```

<br>

## 🛠️ Hermes Skill Integration

Use in conversation:

```
> Summarize this podcast: https://www.xiaoyuzhoufm.com/episode/xxxxx
```

Hermes auto-loads `SKILL.md` and runs the full pipeline.

<br>

## ⚙️ CLI Reference

### transcribe.py

```bash
python scripts/transcribe.py <xiaoyuzhou_url> [output_dir]
```

| Argument | Description | Default |
|----------|-------------|---------|
| URL | Xiaoyuzhou episode link | Required |
| output_dir | Where to save files | `./output` |

### summarize.py

```bash
python scripts/summarize.py <directory>
```

Reads `meta.txt` + `transcript.txt` from the directory, produces `summary.pdf`.

<br>

## 📊 Benchmarks

| Duration | Download | Encode | Transcribe (CPU) | PDF Build | Total |
|----------|----------|--------|------------------|-----------|-------|
| 30 min | ~10s | ~5s | ~10-15 min | ~10s | ~15 min |
| 60 min | ~20s | ~10s | ~20-30 min | ~15s | ~30 min |
| 137 min | ~40s | ~20s | ~45-60 min | ~20s | ~60 min |

> Tested on: Windows 11, Intel Core i7, 16GB RAM

<br>

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| `faster-whisper` not found | `pip install faster-whisper` |
| `xelatex` not found | Install [MiKTeX](https://miktex.org/download), ensure PATH |
| Chinese shows as □ boxes | Verify `C:\Windows\Fonts\simsun.ttc` and `msyh.ttc` exist |
| Transcription too slow | Try `large-v3` model (more accurate, 3× slower) |
| `ffmpeg` not found | Install ffmpeg, add to PATH |

<br>

## 📄 License

MIT © 2024
