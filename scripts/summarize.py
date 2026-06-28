#!/usr/bin/env python3.12
"""
Generate a beautiful Chinese PDF summary from a podcast transcript.

Usage:
    python summarize.py <output_dir>

Expects these files in output_dir:
    - meta.txt: title, url, duration, word_count (one per line)
    - transcript.txt: full transcription text
    - sections.json: structured sections (optional, for manual override)

Output:
    - summary.tex: LaTeX source
    - summary.pdf: compiled PDF
"""

import subprocess
import os
import json
import sys
import shutil
from datetime import datetime


def log(msg):
    print(msg, flush=True)


def read_meta(meta_path):
    """Read metadata file. Returns (title, url, duration_str, word_count_str)."""
    with open(meta_path, encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    title = lines[0] if len(lines) > 0 else "播客摘要"
    url = lines[1] if len(lines) > 1 else ""
    duration_str = lines[2] if len(lines) > 2 else "未知"
    # Try parsing duration — it can be "8243" (seconds) or "137分23秒"
    dur = duration_str
    if duration_str.isdigit():
        secs = int(duration_str)
        dur = f"{secs//60}分{secs%60}秒"
    wc = lines[3] if len(lines) > 3 else str(len(lines) if len(lines) > 3 else 0)
    if wc.isdigit():
        wc = f"{int(wc):,}"
    return title, url, dur, wc


def read_transcript(tx_path):
    """Read transcript, return cleaned body text (without header)."""
    with open(tx_path, encoding="utf-8") as f:
        text = f.read()
    # Remove YAML-like header
    if "---\n" in text:
        parts = text.split("---\n", 1)
        body = parts[1] if len(parts) > 1 else text
    else:
        body = text
    return body.strip()


def split_sections(body, n=6):
    """Split body text into n roughly equal sections."""
    paragraphs = [p.strip() for p in body.split("\n") if len(p.strip()) > 50]
    if not paragraphs:
        return [("内容", body[:5000])]

    per_section = max(1, len(paragraphs) // n)
    sections = []
    for i in range(n):
        start = i * per_section
        end = start + per_section if i < n - 1 else len(paragraphs)
        if start >= len(paragraphs):
            break
        chunk = "\n\n".join(paragraphs[start:end])
        # Extract first sentence as title
        first_sent = chunk.split("。")[0][:40] if "。" in chunk else chunk[:40]
        sections.append((f"第{i+1}部分: {first_sent}...", chunk[:3000]))
    return sections


def extract_quotes(body, n=6):
    """Extract potential quotable sentences from transcript."""
    quotes = []
    sentences = body.replace("！", "。").replace("？", "。").split("。")

    patterns = ["我觉得", "我认为", "其实", "但是", "我看到了",
                "如果你", "整个", "完全不", "太 exciting", "终于"]

    for s in sentences:
        s = s.strip()
        if len(s) < 10 or len(s) > 200:
            continue
        for p in patterns:
            if p in s and s not in quotes:
                quotes.append(s + "。")
                break
        if len(quotes) >= n:
            break
    return quotes[:n]


def build_latex(title, url, duration, word_count, sections, quotes):
    """Build the complete LaTeX document."""
    # Guest name extraction (heuristic)
    guest = title.split("：")[0].split(":")[0].strip()
    guest_desc = "播客嘉宾"
    podcast = "小宇宙播客"

    # Build TOC
    toc_items = ""
    for i, (sec_title, _) in enumerate(sections[:6], 1):
        short_title = sec_title.split(":")[1].strip() if ":" in sec_title else sec_title[:20]
        toc_items += (
            f"        \\color{{primary!30}}\\fontsize{{22}}{{26}}\\bfseries {i:02d} &\n"
            f"        \\large\\bfseries\\color{{primary}} {short_title} \\\\\n"
            f"        & \\footnotesize\\color{{text-muted}} {sec_title[:60]} \\\\[6pt]\n"
        )

    # Build content sections
    sections_tex = ""
    for i, (sec_title, body_text) in enumerate(sections, 1):
        sections_tex += "\\newpage\n"
        sections_tex += (
            "\\begin{tikzpicture}[remember picture,overlay]\n"
            "    \\fill[section-bg] (current page.north west) rectangle ++(\\paperwidth,-0.6cm);\n"
            "\\end{tikzpicture}\n"
        )
        sections_tex += f"\\section{{{sec_title}}}\n\n"
        # Escape LaTeX special chars in body
        body_text = body_text.replace("\\", "\\textbackslash ")
        body_text = body_text.replace("&", "\\&")
        body_text = body_text.replace("%", "\\%")
        body_text = body_text.replace("#", "\\#")
        body_text = body_text.replace("$", "\\$")
        body_text = body_text.replace("_", "\\_")
        body_text = body_text.replace("{", "\\{")
        body_text = body_text.replace("}", "\\}")
        body_text = body_text.replace("~", "\\textasciitilde ")
        body_text = body_text.replace("^", "\\textasciicircum ")
        sections_tex += f"{body_text}\n\n"

    # Build quotes
    quotes_tex = ""
    for i, q in enumerate(quotes[:6], 1):
        # Clean quote text
        q = q.replace("\\", "\\textbackslash ")
        q = q.replace("&", "\\&").replace("%", "\\%")
        q = q.replace("#", "\\#").replace("$", "\\$")
        q = q.replace("_", "\\_").replace("{", "\\{").replace("}", "\\}")
        quotes_tex += (
            f"\\begin{{quotebox}}\n"
            f"    {{\\color{{primary}}\\bfseries {i:02d}}}\\\\[3pt]\n"
            f"    {{\\large {q}}}\n"
            f"\\end{{quotebox}}\n"
            f"\\vspace{{0.4cm}}\n\n"
        )

    date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""\\documentclass[11pt,a4paper]{{article}}

% === PACKAGES ===
\\usepackage[UTF8]{{ctex}}
\\usepackage{{geometry}}
\\usepackage{{xcolor}}
\\usepackage{{titlesec}}
\\usepackage{{fancyhdr}}
\\usepackage{{booktabs}}
\\usepackage[most]{{tcolorbox}}
\\usepackage{{tikz}}
\\usepackage{{setspace}}
\\usepackage{{enumitem}}

% === PAGE SETUP ===
\\geometry{{left=2.5cm, right=2.5cm, top=2.8cm, bottom=2.5cm}}
\\onehalfspacing

% === COLORS ===
\\definecolor{{primary}}{{RGB}}{{22,47,86}}
\\definecolor{{accent}}{{RGB}}{{180,60,50}}
\\definecolor{{bg-quote}}{{RGB}}{{235,240,248}}
\\definecolor{{text-muted}}{{RGB}}{{130,140,155}}
\\definecolor{{teal}}{{RGB}}{{30,120,110}}
\\definecolor{{section-bg}}{{RGB}}{{22,47,86}}

% === FONTS ===
\\setCJKmainfont[Path=C:/Windows/Fonts/, BoldFont=simhei.ttf]{{simsun.ttc}}
\\setCJKsansfont[Path=C:/Windows/Fonts/]{{msyh.ttc}}
\\setmainfont{{Times New Roman}}

% === SECTION STYLING ===
\\titleformat{{\\section}}
    {{\\fontsize{{17}}{{22}}\\bfseries\\color{{white}}}}
    {{\\thesection}}{{0.5em}}{{}}[\\vspace{{-0.8em}}]
\\titlespacing*{{\\section}}{{0pt}}{{16pt}}{{8pt}}

% === TCOLORBOX STYLES ===
\\newtcolorbox{{quotebox}}[1][]{{
    breakable, enhanced,
    colback=bg-quote, colframe=primary!30,
    boxrule=0.4pt, arc=3pt,
    left=12pt, right=12pt, top=10pt, bottom=10pt,
    before skip=10pt, after skip=10pt,
}}

% === HEADER / FOOTER ===
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyfoot[C]{{\\small\\color{{text-muted}} — \\thepage —}}
\\renewcommand{{\\headrulewidth}}{{0.4pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

\\begin{{document}}

% ==================== COVER ====================
\\begin{{titlepage}}
    \\centering
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\fill[primary] (current page.north west) rectangle ++(\\paperwidth,-4cm);
        \\fill[accent] (current page.north west) rectangle ++(\\paperwidth,-4.15cm);
    \\end{{tikzpicture}}
    \\vspace*{{3.5cm}}
    {{\\fontsize{{26}}{{34}}\\bfseries\\color{{white}} {title}\\par}}
    \\vspace{{0.6cm}}
    {{\\Large\\color{{white!80}} {podcast}\\par}}
    \\vspace{{2cm}}
    \\begin{{tcolorbox}}[
        colback=white, colframe=primary!20,
        arc=6pt, boxrule=0.3pt,
        width=0.75\\textwidth, center, enhanced,
    ]
        \\begin{{center}}
            {{\\color{{text-muted}}\\small {podcast}\\par}}
            \\vspace{{0.3cm}}
            {{\\large\\bfseries\\color{{primary}} {guest}\\par}}
            \\vspace{{0.2cm}}
            {{\\color{{text-muted}}\\small {guest_desc}\\par}}
            \\vspace{{0.4cm}}
            {{\\color{{primary!40}}\\rule{{0.4\\textwidth}}{{0.3pt}}\\par}}
            \\vspace{{0.4cm}}
            {{\\footnotesize\\color{{text-muted}} 时长: {duration} \\quad|\\quad 转录: {word_count} 字\\par}}
            {{\\footnotesize\\color{{text-muted}} 本地 faster-whisper · xiaoyuzhou-to-pdf\\par}}
        \\end{{center}}
    \\end{{tcolorbox}}
    \\vfill
    {{\\footnotesize\\color{{text-muted}} {date_str}\\par}}
    \\vspace{{1.5cm}}
\\end{{titlepage}}

% ==================== TOC ====================
\\begin{{titlepage}}
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\fill[section-bg] (current page.north west) rectangle ++(\\paperwidth,-2.8cm);
    \\end{{tikzpicture}}
    \\vspace*{{2.5cm}}
    {{\\fontsize{{24}}{{30}}\\bfseries\\color{{white}} 目录\\par}}
    \\vspace{{0.3cm}}
    {{\\large\\color{{white!70}} CONTENTS\\par}}
    \\vspace{{1.8cm}}
    \\begin{{center}}
    \\renewcommand{{\\arraystretch}}{{2.0}}
    \\begin{{tabular}}{{@{{}}r p{{11cm}}@{{}}}}
{toc_items}
    \\end{{tabular}}
    \\end{{center}}
    \\vfill
    \\begin{{flushright}}
        {{\\footnotesize\\color{{text-muted}} 全文转录 {word_count} 字\\par}}
    \\end{{flushright}}
\\end{{titlepage}}

% ==================== CONTENT ====================
{sections_tex}

% ==================== QUOTES ====================
\\newpage
\\begin{{tikzpicture}}[remember picture,overlay]
    \\fill[section-bg] (current page.north west) rectangle ++(\\paperwidth,-0.6cm);
\\end{{tikzpicture}}
\\section{{核心金句}}
\\vspace{{0.5cm}}
{quotes_tex}
\\vspace{{1cm}}
\\begin{{center}}
    {{\\footnotesize\\color{{text-muted}}
    — 全文转录 {word_count} 字 \\quad|\\quad xiaoyuzhou-to-pdf \\quad|\\quad {date_str} —}}
\\end{{center}}

\\end{{document}}
"""


def compile_pdf(tex_path, output_dir):
    """Compile .tex to .pdf using xelatex. Two passes for cross-refs."""
    basename = "summary"
    for _ in range(2):
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode",
             f"-job-name={basename}", tex_path],
            cwd=output_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        if "did not succeed" in result.stdout + result.stderr:
            log(f"⚠️  LaTeX 编译有警告（可能不影响输出）")
    return os.path.join(output_dir, f"{basename}.pdf")


def main():
    if len(sys.argv) < 2:
        print("Usage: python summarize.py <output_dir>")
        sys.exit(1)

    output_dir = sys.argv[1]
    os.makedirs(output_dir, exist_ok=True)

    meta_path = os.path.join(output_dir, "meta.txt")
    tx_path = os.path.join(output_dir, "transcript.txt")

    if not os.path.exists(meta_path) or not os.path.exists(tx_path):
        log("❌ 缺少 meta.txt 或 transcript.txt，请先运行 transcribe.py")
        sys.exit(1)

    title, url, duration, word_count = read_meta(meta_path)
    body = read_transcript(tx_path)

    log(f"📝 {title}")
    log(f"📊 {word_count} 字, {duration}")

    # Generate sections and quotes
    sections = split_sections(body)
    quotes = extract_quotes(body)
    log(f"📋 {len(sections)} 章节, {len(quotes)} 金句")

    # Build LaTeX
    tex_content = build_latex(title, url, duration, word_count, sections, quotes)

    tex_path = os.path.join(output_dir, "summary.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex_content)
    log(f"📄 LaTeX: {tex_path}")

    # Compile
    log("🔨 编译 PDF (XeLaTeX)...")
    pdf_path = compile_pdf(tex_path, output_dir)
    log(f"✅ PDF: {pdf_path}")

    # Cleanup aux files
    for ext in [".aux", ".log", ".out", ".toc"]:
        f = os.path.join(output_dir, f"summary{ext}")
        if os.path.exists(f):
            os.remove(f)


if __name__ == "__main__":
    main()
