"""
Convert ROADMAP_Day1-15.md into ROADMAP_Day1-15.pdf (ReportLab).

Run:
  python generate_roadmap_pdf.py
"""

from __future__ import annotations

import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas


MD_PATH = "ROADMAP_Day1-15.md"
PDF_PATH = "ROADMAP_Day1-15.pdf"


def clean_line(line: str) -> str:
    # Make markdown readable in plain PDF text.
    line = line.replace("`", "'")
    line = re.sub(r"^\s*#+\s*", "", line)  # remove leading headers
    line = line.replace("**", "")
    return line.strip()


def wrap_text(text: str, c: Canvas, font_name: str, font_size: float, max_width: float) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    current = ""

    for word in words:
        candidate = word if not current else f"{current} {word}"
        w = pdfmetrics.stringWidth(candidate, font_name, font_size)
        if w <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines if lines else [""]


def main() -> None:
    if not os.path.exists(MD_PATH):
        raise SystemExit(f"Missing {MD_PATH}. Run this script from the project folder.")

    c = Canvas(PDF_PATH, pagesize=A4)
    page_w, page_h = A4

    left = 40
    right = 40
    top = 40
    bottom = 40
    usable_w = page_w - left - right

    y = page_h - top
    line_h = 13

    title_font = "Helvetica-Bold"
    normal_font = "Helvetica"
    c.setTitle("ROADMAP_Day1-15")

    title = "Crop Recommendation Project Roadmap (Day 1 to Day 15)"
    c.setFont(title_font, 14)
    for tl in wrap_text(title, c, title_font, 14, usable_w):
        if y < bottom + line_h:
            c.showPage()
            y = page_h - top
        c.drawString(left, y, tl)
        y -= line_h
    y -= 6

    c.setFont(normal_font, 10)
    with open(MD_PATH, "r", encoding="utf-8") as f:
        for raw in f.read().splitlines():
            if not raw.strip():
                y -= line_h // 2
                continue

            line = clean_line(raw)
            for wl in wrap_text(line, c, normal_font, 10, usable_w):
                if y < bottom + line_h:
                    c.showPage()
                    c.setFont(normal_font, 10)
                    y = page_h - top
                c.drawString(left, y, wl)
                y -= line_h

    c.save()
    print(f"Generated: {PDF_PATH}")


if __name__ == "__main__":
    main()

