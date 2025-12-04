import sys
from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTChar, LTRect, LTLine

"""
Usage:
  python tools/extract_header_coords.py <path_to_reference_pdf>
Outputs:
  Prints header-related rectangles and text boxes with exact coordinates (points) and sizes.
Notes:
  - PDF coordinates are in points (1 pt = 1/72 inch). For mm, use: mm = pts * 25.4 / 72
  - This script looks for the top band and header grid elements: labels like
    'DATA DO RECEBIMENTO', 'IDENTIFICAÇÃO E ASSINATURA DO RECEBEDOR', 'NF-e', 'DANFE', 'CHAVE DE ACESSO'.
"""

PT_TO_MM = 25.4 / 72.0

def to_mm(v):
    return round(v * PT_TO_MM, 3)


def main(pdf_path: Path):
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    print("=== Extracting header coords ===")
    for page_layout in extract_pages(str(pdf_path)):
        # Collect rects and text in the top ~120mm of the page
        page_height = page_layout.height
        top_limit_pts = 120 / PT_TO_MM  # convert mm back to points
        rects = []
        texts = []
        lines = []

        for element in page_layout:
            if isinstance(element, LTRect):
                # Filter near top
                y = element.y0
                if page_height - y <= top_limit_pts:
                    rects.append(element)
            elif isinstance(element, LTLine):
                y = element.y0
                if page_height - y <= top_limit_pts:
                    lines.append(element)
            elif isinstance(element, LTTextBoxHorizontal):
                # Check each char bbox to approximate bounding box
                y = element.y0
                if page_height - y <= top_limit_pts:
                    texts.append(element)

        print(f"Rects: {len(rects)} | Lines: {len(lines)} | Texts: {len(texts)}")

        def dump_rect(r: LTRect, name="rect"):
            print(f"{name}: x={to_mm(r.x0):.2f}mm, y_from_top={to_mm(page_height - r.y0):.2f}mm, w={to_mm(r.width):.2f}mm, h={to_mm(r.height):.2f}mm")

        # Dump likely header rects by size thresholds
        for i, r in enumerate(sorted(rects, key=lambda e: (-e.height, -e.width))[:50]):
            dump_rect(r, name=f"rect[{i}]")

        # Dump texts with content
        for tb in texts:
            txt = tb.get_text().strip().replace("\n", " ")
            if not txt:
                continue
            x = to_mm(tb.x0)
            y_from_top = to_mm(page_height - tb.y0)
            w = to_mm(tb.width)
            h = to_mm(tb.height)
            print(f"text: '{txt}' | x={x:.2f}mm y_from_top={y_from_top:.2f}mm w={w:.2f}mm h={h:.2f}mm")

        # Only first page needed
        break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/extract_header_coords.py <path_to_reference_pdf>")
        sys.exit(1)
    main(Path(sys.argv[1]))
