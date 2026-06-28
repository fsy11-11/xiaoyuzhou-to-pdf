#!/usr/bin/env python3.12
"""
Download and transcribe a Xiaoyuzhou podcast episode using local faster-whisper.

Usage:
    python transcribe.py <xiaoyuzhou_url> [output_dir]

Example:
    python transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxxxx" ./output
"""

import subprocess
import os
import re
import sys
import time
import shutil


def log(msg):
    print(msg, flush=True)


def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <xiaoyuzhou_url> [output_dir]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    tmp = os.path.join(os.environ.get("TEMP", "/tmp"), f"xz_transcribe_{os.getpid()}")
    os.makedirs(tmp, exist_ok=True)

    # ── 1. Parse page ──
    log("📻 解析页面...")
    html = subprocess.run(["curl", "-s", "-L", url],
                          capture_output=True, text=True, timeout=30).stdout

    audio_urls = re.findall(r'https://media\.xyzcdn\.net/[^"]*\.(?:m4a|mp3)', html)
    titles = re.findall(r'"title":"([^"]*)"', html)

    if not audio_urls:
        log("❌ 无法从页面提取音频链接")
        sys.exit(1)

    title = titles[0] if titles else "Untitled"
    audio_url = audio_urls[0]

    log(f"📝 标题: {title}")
    log(f"🔗 音频: {audio_url[:60]}...")

    # ── 2. Download ──
    log("⬇️  下载音频...")
    audio_path = os.path.join(tmp, "original.m4a")
    subprocess.run(["curl", "-sL", "-o", audio_path, audio_url],
                   check=True, timeout=300)
    size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    log(f"📦 {size_mb:.0f}MB")

    # ── 3. Duration ──
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", audio_path],
        capture_output=True, text=True
    )
    dur_sec = int(float(result.stdout.strip()))
    dur_str = f"{dur_sec // 60}分{dur_sec % 60}秒"
    log(f"⏱️  {dur_str}")

    # ── 4. Transcode to 64k mono mp3 ──
    log("🔄 转码 64k mono...")
    mono_path = os.path.join(tmp, "mono.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", audio_path, "-b:a", "64k", "-ac", "1", mono_path],
        capture_output=True, check=True
    )
    mono_mb = os.path.getsize(mono_path) / (1024 * 1024)
    log(f"📦 转码后: {mono_mb:.0f}MB")

    # ── 5. Transcribe ──
    log("🎙️  转录中 (faster-whisper medium)...")
    log("    ⚠️  首次运行会下载模型 (~1.5GB)，请耐心等待")

    from faster_whisper import WhisperModel

    model = WhisperModel("medium", device="cpu", compute_type="int8")
    segments, info = model.transcribe(mono_path, language="zh",
                                       beam_size=5, vad_filter=True)

    log(f"    检测语言: {info.language} (概率: {info.language_probability:.2%})")

    # Collect all segments
    texts = []
    total_words = 0
    for seg in segments:
        texts.append(seg.text)
        total_words += 1
        if total_words % 50 == 0:
            log(f"    ...已转录 {total_words} 个片段", end="\r")

    text = " ".join(texts)
    char_count = len(text)

    # ── 6. Save ──
    tx_path = os.path.join(output_dir, "transcript.txt")
    with open(tx_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"来源: {url}\n")
        f.write(f"时长: {dur_str}\n")
        f.write(f"字数: {char_count}\n\n")
        f.write("---\n\n")
        f.write(text)

    log(f"\n✅ 转录完成！{char_count} 字")

    # Save metadata for PDF generation
    meta_path = os.path.join(output_dir, "meta.txt")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n{url}\n{dur_str}\n{char_count}\n")

    log(f"📄 转录文本: {tx_path}")
    log(f"📋 元数据:   {meta_path}")

    # Cleanup temp
    shutil.rmtree(tmp, ignore_errors=True)

    return tx_path


if __name__ == "__main__":
    main()
