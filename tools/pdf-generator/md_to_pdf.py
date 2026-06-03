#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["markdown==3.6", "pygments==2.18.0"]
# ///
"""
md_to_pdf.py — Convert a Markdown file to a brand-letterhead PDF via Chrome headless.

Usage:
    uvx --from .  python tools/pdf-generator/md_to_pdf.py INPUT.md OUTPUT.pdf [TITLE]
or:
    uv run --no-project --with markdown --with pygments tools/pdf-generator/md_to_pdf.py INPUT.md OUTPUT.pdf [TITLE]

This script reads a Markdown file, renders it to HTML with a LedgerProof
brand letterhead inlined, writes a temp HTML file, then invokes Chrome in
headless mode to produce a PDF. No external network calls; suitable for
internal-strategy docs.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import markdown


# Brand letterhead (text-only — keeps PDF small, no external image deps)
LETTERHEAD_HTML = """
<header class="letterhead">
  <div class="brand">
    <div class="brand-mark">LP</div>
    <div class="brand-text">
      <div class="brand-name">LedgerProof Foundation</div>
      <div class="brand-tagline">EU AI Act Article 50 — open cryptographic transparency receipts</div>
    </div>
  </div>
  <div class="brand-meta">
    <div>Document classification: <b>Internal — strategic planning</b></div>
    <div>Generated: {generated_date}</div>
  </div>
</header>
"""

STYLES = """
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 22mm 16mm;
    @bottom-left { content: "LedgerProof Foundation — Internal Strategic Planning"; font: 9pt sans-serif; color: #6b7280; }
    @bottom-right { content: "Page " counter(page) " of " counter(pages); font: 9pt sans-serif; color: #6b7280; }
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.42;
    color: #111827;
    max-width: 720pt;
    margin: 0 auto;
    padding: 0;
  }
  header.letterhead {
    border-bottom: 2px solid #0b3d2e;
    padding-bottom: 10pt;
    margin-bottom: 16pt;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    page-break-after: avoid;
  }
  .brand { display: flex; gap: 10pt; align-items: center; }
  .brand-mark {
    width: 36pt; height: 36pt;
    background: #0b3d2e; color: #f59e0b;
    font-weight: 800; font-size: 18pt;
    display: flex; align-items: center; justify-content: center;
    border-radius: 4pt;
    letter-spacing: -1pt;
  }
  .brand-name { font-weight: 700; font-size: 12pt; color: #0b3d2e; }
  .brand-tagline { font-size: 8.5pt; color: #4b5563; margin-top: 1pt; }
  .brand-meta { font-size: 8.5pt; color: #4b5563; text-align: right; line-height: 1.45; }
  h1 { font-size: 18pt; color: #0b3d2e; border-bottom: 1px solid #e5e7eb; padding-bottom: 4pt; margin-top: 16pt; margin-bottom: 8pt; page-break-after: avoid; }
  h2 { font-size: 14pt; color: #0b3d2e; margin-top: 14pt; margin-bottom: 6pt; page-break-after: avoid; }
  h3 { font-size: 11.5pt; color: #1f2937; margin-top: 10pt; margin-bottom: 4pt; page-break-after: avoid; }
  h4 { font-size: 10.5pt; color: #1f2937; margin-top: 8pt; margin-bottom: 3pt; page-break-after: avoid; }
  p, ul, ol { margin-top: 4pt; margin-bottom: 6pt; }
  code { font-family: "SF Mono", "Menlo", Consolas, monospace; font-size: 8.5pt; background: #f3f4f6; padding: 1pt 3pt; border-radius: 2pt; }
  pre { background: #f3f4f6; padding: 8pt; border-radius: 4pt; overflow-x: auto; font-size: 8pt; line-height: 1.35; page-break-inside: avoid; }
  pre code { background: transparent; padding: 0; font-size: 8pt; }
  table { border-collapse: collapse; margin: 8pt 0; font-size: 8.5pt; width: 100%; page-break-inside: avoid; }
  th, td { border: 1px solid #d1d5db; padding: 4pt 6pt; text-align: left; vertical-align: top; }
  th { background: #0b3d2e; color: #fbbf24; font-weight: 600; }
  tr:nth-child(even) td { background: #f9fafb; }
  blockquote { border-left: 3px solid #f59e0b; padding-left: 10pt; color: #4b5563; margin: 8pt 0; font-style: italic; }
  hr { border: 0; border-top: 1px solid #e5e7eb; margin: 14pt 0; }
  a { color: #0b3d2e; text-decoration: underline; }
  ul li, ol li { margin-bottom: 2pt; }
  strong { color: #0b3d2e; }
  .footer-note { margin-top: 18pt; padding-top: 8pt; border-top: 1px solid #e5e7eb; font-size: 8pt; color: #6b7280; }
</style>
"""

FOOTER_HTML = """
<div class="footer-note">
  <p><b>Document boundary:</b> This document is internal strategic planning material for LedgerProof Foundation (501(c)(3) in formation, Delaware) and LedgerProof Inc. (Delaware C-corp). It contains assumptions, forecasts, and decisions that may change as conditions evolve. Numbers labeled BASE / STRETCH / DOWNSIDE are scenarios, not forecasts. Distribution is limited to Foundation board, Inc. officers, and named diligence counterparties under NDA or equivalent.</p>
  <p><b>Confidentiality:</b> Do not redistribute without consent of the founder. Bitcoin-anchored governance receipts apply only to ratified Foundation actions; this document is a planning artifact and is NOT receipt-anchored.</p>
</div>
"""


def render_html(md_path: Path, title: str | None) -> str:
    md_text = md_path.read_text(encoding="utf-8")
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "codehilite",
            "toc",
            "sane_lists",
            "attr_list",
        ],
        extension_configs={"codehilite": {"guess_lang": False, "noclasses": True}},
    )
    body_html = md.convert(md_text)

    doc_title = title or md_path.stem
    generated_date = datetime.utcnow().strftime("%Y-%m-%d UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{doc_title}</title>
{STYLES}
</head>
<body>
{LETTERHEAD_HTML.format(generated_date=generated_date)}
<main>
{body_html}
</main>
{FOOTER_HTML}
</body>
</html>
"""


def find_chrome() -> str:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise SystemExit("ERROR: Chrome/Chromium not found")


def html_to_pdf(html: str, output: Path) -> None:
    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        html_file = td_path / "doc.html"
        html_file.write_text(html, encoding="utf-8")
        # Chrome wants file:// URL
        url = f"file://{html_file.resolve()}"
        out_path = output.resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--virtual-time-budget=10000",
            f"--print-to-pdf={out_path}",
            url,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0 or not out_path.exists():
            sys.stderr.write(result.stderr)
            raise SystemExit(f"ERROR: Chrome PDF generation failed (rc={result.returncode})")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path, help="Input markdown file")
    p.add_argument("output", type=Path, help="Output PDF path")
    p.add_argument("--title", type=str, default=None, help="Document title (defaults to filename)")
    args = p.parse_args()

    if not args.input.exists():
        raise SystemExit(f"ERROR: input file not found: {args.input}")

    html = render_html(args.input, args.title)
    html_to_pdf(html, args.output)
    size = args.output.stat().st_size
    print(f"✓ {args.input.name} → {args.output} ({size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
