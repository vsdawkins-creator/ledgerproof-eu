"""Artifact builders that produce shippable bytes.

Each builder takes a rendered template and produces HTML (always) and
optionally PDF (via WeasyPrint when available). Output paths are returned
so callers can attach to email, upload to marketplace, or anchor.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from gtm import brand
from gtm.rendering import render_one_pager


_HTML_SHELL = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    @page {{ size: A4; margin: 18mm; }}
    body {{
      background: {bg};
      color: {navy};
      font-family: {sans};
      line-height: 1.5;
      max-width: 720px;
      margin: 0 auto;
      padding: 32px;
    }}
    h1, h2, h3 {{ font-family: {display}; color: {navy}; }}
    h1 {{ border-bottom: 3px solid {mint}; padding-bottom: 8px; }}
    a {{ color: {navy}; text-decoration: underline; text-decoration-color: {mint}; }}
    code {{ font-family: {mono}; background: rgba(8,20,36,0.04); padding: 1px 4px; }}
    .footer {{
      margin-top: 32px; padding-top: 12px;
      border-top: 1px solid rgba(8,20,36,0.15);
      font-size: 0.85em; color: rgba(8,20,36,0.7);
    }}
  </style>
</head>
<body>
{content}
<div class="footer">
  Anchored as LedgerProof Receipt. Verify at
  <a href="https://verify.ledgerproofhq.io/r/{receipt_id}">verify.ledgerproofhq.io</a>.
</div>
</body>
</html>
"""


@dataclass(frozen=True)
class BuiltArtifact:
    slug: str
    html_path: Path
    pdf_path: Path | None
    title: str


def _markdown_to_html(md: str) -> str:
    """Lightweight Markdown-to-HTML conversion. Avoids adding a heavy
    Markdown dependency; covers headings, paragraphs, lists, code, links,
    and bold/italic — which is all our templates use.
    """
    import re

    lines = md.strip().split("\n")
    html_parts: list[str] = []
    in_list = False
    in_para: list[str] = []

    def flush_para() -> None:
        if in_para:
            text = " ".join(in_para).strip()
            text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
            text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
            text = re.sub(
                r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text
            )
            html_parts.append(f"<p>{text}</p>")
            in_para.clear()

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    for raw in lines:
        line = raw.rstrip()
        if not line:
            flush_para()
            close_list()
            continue
        if line.startswith("### "):
            flush_para()
            close_list()
            html_parts.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            flush_para()
            close_list()
            html_parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            flush_para()
            close_list()
            html_parts.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("- "):
            flush_para()
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line[2:])
            item = re.sub(r"`([^`]+)`", r"<code>\1</code>", item)
            html_parts.append(f"<li>{item}</li>")
        elif line.startswith("---"):
            flush_para()
            close_list()
            html_parts.append("<hr>")
        else:
            in_para.append(line)
    flush_para()
    close_list()
    return "\n".join(html_parts)


def build_one_pager(
    slug: str,
    *,
    title: str,
    receipt_id: str,
    output_dir: Path,
    context: dict | None = None,
) -> BuiltArtifact:
    md = render_one_pager(slug, context=context)
    body_html = _markdown_to_html(md)
    full_html = _HTML_SHELL.format(
        title=title,
        bg=brand.COLORS.bg,
        navy=brand.COLORS.navy,
        mint=brand.COLORS.mint,
        sans=brand.FONTS.sans,
        display=brand.FONTS.display,
        mono=brand.FONTS.mono,
        content=body_html,
        receipt_id=receipt_id,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / f"{slug}.html"
    html_path.write_text(full_html, encoding="utf-8")

    pdf_path: Path | None = None
    try:
        from weasyprint import HTML  # type: ignore

        pdf_path = output_dir / f"{slug}.pdf"
        HTML(string=full_html).write_pdf(str(pdf_path))
    except Exception:
        # WeasyPrint requires system libs; surface as PDF-missing, not as failure
        pdf_path = None

    return BuiltArtifact(slug=slug, html_path=html_path, pdf_path=pdf_path, title=title)


def stamp_summary_html(
    *,
    customer: str,
    coverage_start: date,
    coverage_end: date,
    receipt_count: int,
    bitcoin_block_low: int,
    bitcoin_block_high: int,
    stamp_id: str,
    coverage_table: list[tuple[str, str, int]],
) -> str:
    """Render the Audit-Ready Compliance Stamp summary as HTML.

    The full one-page A4 PDF is generated by the production stamp pipeline
    (see 09-code-plan/day-90/02-stamp-pdf-pipeline.md). This renders the
    machine-readable HTML summary used in customer dashboard and email.
    """
    rows = "\n".join(
        f'<tr><td>{reg}</td><td>{clause}</td><td style="text-align:right">{n:,}</td></tr>'
        for (reg, clause, n) in coverage_table
    )
    return _HTML_SHELL.format(
        title=f"Compliance Stamp — {customer}",
        bg=brand.COLORS.bg,
        navy=brand.COLORS.navy,
        mint=brand.COLORS.mint,
        sans=brand.FONTS.sans,
        display=brand.FONTS.display,
        mono=brand.FONTS.mono,
        content=f"""
        <h1>Audit-Ready Compliance Stamp</h1>
        <p><strong>Customer:</strong> {customer}</p>
        <p><strong>Coverage:</strong> {coverage_start.isoformat()} to {coverage_end.isoformat()}</p>
        <p><strong>Receipts:</strong> {receipt_count:,}</p>
        <p><strong>Bitcoin block range:</strong> {bitcoin_block_low:,}—{bitcoin_block_high:,}</p>
        <p><strong>Stamp ID:</strong> <code>{stamp_id}</code></p>
        <table style="width:100%;border-collapse:collapse;margin-top:16px;">
          <thead>
            <tr style="border-bottom:2px solid {brand.COLORS.mint};">
              <th align="left">Regulation</th>
              <th align="left">Sub-clause</th>
              <th align="right">Receipts</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        """,
        receipt_id=stamp_id,
    )
