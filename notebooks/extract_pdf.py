#!/usr/bin/env python3
"""
Extract the "Pre-monsoon Depth to Ground Water Level" tables from
Pre-monsoon_WL_1994-2025.pdf (10,270 pages) into a single CSV.

Requires:
    * poppler-utils  (the `pdftotext` command)
    * pdfplumber     (pip install pdfplumber)  -- only used for the ~170 pages
                     that contain wrapped / overlapping text cells

Usage:
    python extract_wl_to_csv.py Pre-monsoon_WL_1994-2025.pdf output.csv

Output columns:
    State, District, Block, Village, Latitude, Longitude, Date, WL_mbgl
Date is written as ISO yyyy-mm-dd (the PDF has dd-mm-yy; 2-digit years < 50 -> 20xx).

Method
------
1. FAST PATH (most pages): `pdftotext -layout` for the whole PDF. Each page repeats
   a header line (two spellings exist in this file), and its column positions are
   used to slice State/District/Block/Village. Latitude/Longitude/Date/WL are
   parsed from the right end of the row with a regex.
2. SLOW PATH (pages where a row is split over several lines, or long text spills
   into the next column): the layout text is unreliable there, so those pages are
   re-read with pdfplumber. In the PDF's drawing order every cell's characters are
   contiguous, so cells are rebuilt as runs of touching characters, and each cell
   is assigned to a column by its x-position.
"""
import csv
import re
import subprocess
import sys
from datetime import date

OUT_HEADER = ["State", "District", "Block", "Village",
              "Latitude", "Longitude", "Date", "WL_mbgl"]
HEADER_RE = re.compile(r"^\s*(State|STATE_UT)\b")
TAIL_RE = re.compile(
    r"\s(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s+(\d{1,2}-\d{1,2}-\d{2,4})\s*(\S*)\s*$"
)
DATE_RE = re.compile(r"^\d{1,2}-\d{1,2}-\d{2,4}$")
NUM_RE = re.compile(r"^-?\d+(?:\.\d+)?$")


def iso_date(s):
    d, m, y = s.split("-")
    y = int(y)
    if y < 100:
        y += 2000 if y < 50 else 1900
    try:
        return date(y, int(m), int(d)).isoformat()
    except ValueError:
        return s


# ---------------------------------------------------------------- fast path
def page_needs_slow_path(page_text):
    """True if any data line is not a clean single-line row."""
    seen_header = False
    for line in page_text.split("\n"):
        if not line.strip():
            continue
        if HEADER_RE.match(line):
            seen_header = True
            continue
        if "Ground Water Level Data" in line:
            continue
        if not seen_header:
            return True
        if not TAIL_RE.search(line) or line[0].isspace():
            return True
        left = line[: TAIL_RE.search(line).start()].strip()
        if len(re.split(r"\s{2,}", left)) != 4:
            return True
    return False


def parse_page_layout(page_text):
    rows, starts = [], None
    for line in page_text.split("\n"):
        if not line.strip() or "Ground Water Level Data" in line:
            continue
        if HEADER_RE.match(line):
            starts = [t.start() for t in re.finditer(r"\S+", line)][:4]
            continue
        m = TAIL_RE.search(line)
        left = line[: m.start()]
        bounds = starts + [len(left) + 1]
        vals = [left[bounds[i]:bounds[i + 1]].strip() for i in range(4)]
        rows.append(vals + [m.group(1), m.group(2), iso_date(m.group(3)), m.group(4)])
    return rows


# ---------------------------------------------------------------- slow path
def assign_columns(text_cells, col_x):
    """Map the text cells of one record to State/District/Block/Village by x."""
    cols = [max((k for k in range(4) if col_x[k] <= c[0] + 1.0), default=0)
            for c in text_cells]
    merged = []                       # [column, text]
    for col, (_x0, txt, _x1) in zip(cols, text_cells):
        if merged and col <= merged[-1][0]:
            # same/backward column: either a wrapped cell or a cell that was split
            # by coincidence at a column edge -> fold it into the previous piece,
            # except a split-off piece which belongs to the cell before it
            if len(merged) >= 2 and col == merged[-1][0] and merged[-2][0] < col:
                merged[-2][1] += merged[-1][1]      # false split: glue back
                merged[-1] = [col, txt]
            else:
                merged[-1][1] += " " + txt
        else:
            merged.append([col, txt])
    vals = [""] * 4
    for col, txt in merged:
        vals[col] = (vals[col] + " " + txt).strip()
    return vals


def parse_page_plumber(page):
    words = page.extract_words()
    # header: the line whose first word is State / STATE_UT
    hdr = next(w for w in words if w["text"] in ("State", "STATE_UT"))
    line = [w for w in words if abs(w["top"] - hdr["top"]) < 2]
    col_x = sorted(w["x0"] for w in line)[:4]          # left edge of 4 text columns

    # 1) rebuild cells = runs of touching characters, in drawing order.
    #    A cell that overflows exactly up to the next column's left edge would
    #    touch it, so also break where a character starts exactly on a column edge.
    cells, cur, prev = [], [], None
    for ch in page.chars:
        if prev is not None:
            gap = abs(ch["x0"] - prev["x1"]) > 1.5
            at_edge = (ch["text"].strip() and prev["text"].strip()
                       and any(abs(ch["x0"] - cx) < 0.15 and cur[0]["x0"] < cx - 1.0
                               for cx in col_x[1:]))
            if gap or at_edge:
                cells.append(cur)
                cur = []
        cur.append(ch)
        prev = ch
    if cur:
        cells.append(cur)
    cells = [(c[0]["x0"], re.sub(r"\s+", " ", "".join(k["text"] for k in c)).strip(), c[-1]["x1"])
             for c in cells]
    cells = [c for c in cells if c[1] and "Ground Water Level Data" not in c[1]]

    # 2) group cells into records: a record ends with its date cell (+ optional WL)
    rows, buf, i = [], [], 0
    seen_hdr = False
    while i < len(cells):
        x0, txt, x1 = cells[i]
        if not seen_hdr:                    # skip title + header cells
            if txt.startswith("WL"):
                seen_hdr = True
            i += 1
            continue
        buf.append(cells[i])
        i += 1
        if DATE_RE.match(txt):
            wl = ""
            if i < len(cells) and cells[i][0] > x0 + 20:   # WL sits well right of the date
                wl = cells[i][1]
                i += 1
            lat_c, lon_c, date_c = buf[-3], buf[-2], buf[-1]
            text_cells = buf[:-3]
            vals = assign_columns(text_cells, col_x)
            rows.append(vals + [lat_c[1], lon_c[1], iso_date(date_c[1]), wl])
            buf = []
    return rows, len(buf)


def main(pdf_path, csv_path):
    print("Running pdftotext -layout ...", flush=True)
    text = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], check=True,
                          capture_output=True, encoding="utf-8", errors="replace").stdout
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()

    slow = [i for i, p in enumerate(pages) if page_needs_slow_path(p)]
    print(f"{len(pages):,} pages; {len(slow)} need the slower pdfplumber pass", flush=True)

    slow_rows = {}
    if slow:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for i in slow:
                slow_rows[i], leftover = parse_page_plumber(pdf.pages[i])
                if leftover:
                    print(f"  warning: page {i + 1}: {leftover} trailing cells not in a row")

    n = 0
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(OUT_HEADER)
        for i, p in enumerate(pages):
            rows = slow_rows[i] if i in slow_rows else parse_page_layout(p)
            w.writerows(rows)
            n += len(rows)
    print(f"Done: {n:,} rows -> {csv_path}")


if __name__ == "__main__":
    main("../raw/Pre-monsoon_WL_1994-2025.pdf", "../raw/groundwater")
