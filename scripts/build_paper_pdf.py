#!/usr/bin/env python3
"""Build paper/character_hold_arxiv.pdf from paper/manuscript.md (fpdf2; no system LaTeX)."""

from __future__ import annotations

import re
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
MD = PAPER / "manuscript.md"
OUT = PAPER / "character_hold_arxiv.pdf"

REPL = {
    "—": "-",
    "–": "-",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "×": "x",
    "≈": "~",
    "Δ": "Delta-",
    "κ": "kappa",
    "→": "->",
    "←": "<-",
    "≥": ">=",
    "≤": "<=",
    "≠": "!=",
    "·": "-",
    "…": "...",
}


def clean(s: str) -> str:
    for a, b in REPL.items():
        s = s.replace(a, b)
    s = re.sub(r"[*_`]+", "", s)
    return s.encode("latin-1", "replace").decode("latin-1")


class PDF(FPDF):
    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 8, f"{self.page_no()}", align="C")


def main() -> None:
    md = MD.read_text(encoding="utf-8")
    if md.startswith("---"):
        md = md.split("---", 2)[2]

    pdf = PDF(format="A4")
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.multi_cell(
        0,
        6,
        clean(
            "Character-shaped prompts under pressure: "
            "disposition cards vs matched instructions"
        ),
    )
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, clean("Federico Cavaletto | 2026 | Preprint candidate (arXiv TBD)"))
    pdf.ln(3)

    in_code = False
    for line in md.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        text = clean(line)
        usable = pdf.epw
        if in_code:
            pdf.set_font("Courier", "", 7)
            pdf.multi_cell(usable, 3.5, text or " ")
            continue
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if m:
            cap, path = m.group(1), m.group(2)
            img = PAPER / path
            if img.exists():
                pdf.ln(2)
                pdf.image(str(img), w=min(174, usable))
                pdf.set_font("Helvetica", "I", 8)
                pdf.multi_cell(usable, 4, clean(cap))
                pdf.ln(1)
            continue
        if line.startswith("## "):
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(usable, 5, clean(line[3:]))
            pdf.ln(1)
            continue
        if line.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(usable, 5, clean(line[4:]))
            continue
        if line.strip().startswith("|"):
            if set(line.strip()) <= set("|- :") or "---" in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            pdf.set_font("Helvetica", "", 7)
            pdf.multi_cell(usable, 3.5, clean(" | ".join(cells)))
            continue
        if not line.strip():
            pdf.ln(1.5)
            continue
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(usable, 4.5, text)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {pdf.pages_count} pages)")


if __name__ == "__main__":
    main()
