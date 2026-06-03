from pathlib import Path

from indicators import INDICATORS


ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "informe.md"
PDF_PATH = ROOT / "informe.pdf"


def build_markdown():
    lines = [
        "# Informe de Indicadores - Lab 7 Visualización de Datos",
        "",
        "**Área asignada:** Ventas",
        "",
        "Todos los indicadores fueron diseñados para Metabase usando Native Query / SQL sobre PostgreSQL.",
        "",
    ]
    for idx, indicator in enumerate(INDICATORS, 1):
        lines.extend(
            [
                f"## {idx}. {indicator['name']}",
                "",
                f"1. **Nombre del indicador:** {indicator['name']}",
                f"2. **Qué representa en términos de negocio:** {indicator['business']}",
                f"3. **Por qué es importante para el área de Ventas:** {indicator['importance']}",
                f"4. **Qué tipo de visualización se usó y por qué es la más adecuada:** {indicator['visualization']}",
                "5. **Consulta SQL completa usada para generarlo en Metabase:**",
                "",
                "```sql",
                indicator["sql"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def escape_pdf_text(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_text(text, max_chars):
    if not text:
        return [""]
    wrapped = []
    for raw_line in text.splitlines():
        words = raw_line.split(" ")
        line = ""
        for word in words:
            candidate = word if not line else f"{line} {word}"
            if len(candidate) <= max_chars:
                line = candidate
            else:
                if line:
                    wrapped.append(line)
                while len(word) > max_chars:
                    wrapped.append(word[:max_chars])
                    word = word[max_chars:]
                line = word
        wrapped.append(line)
    return wrapped


def markdown_to_plain_lines(markdown):
    lines = []
    for line in markdown.splitlines():
        clean = (
            line.replace("**", "")
            .replace("```sql", "SQL:")
            .replace("```", "")
            .replace("# ", "")
            .replace("## ", "")
        )
        if clean.startswith("- "):
            clean = clean[2:]
        lines.extend(wrap_text(clean, 100))
    return lines


def make_pdf(lines):
    pages = []
    current = []
    for line in lines:
        if len(current) >= 46:
            pages.append(current)
            current = []
        current.append(line)
    if current:
        pages.append(current)

    objects = []
    page_ids = []
    font_id = 3
    for page in pages:
        stream_lines = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
        first = True
        for line in page:
            if not first:
                stream_lines.append("T*")
            first = False
            stream_lines.append(f"({escape_pdf_text(line)}) Tj")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines).encode("latin-1", errors="replace")
        content_id = len(objects) + 4
        page_id = len(objects) + 5
        objects.append(f"{content_id} 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream\nendobj\n")
        objects.append(
            f"{page_id} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>\nendobj\n".encode("latin-1")
        )
        page_ids.append(page_id)

    header_objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        f"2 0 obj\n<< /Type /Pages /Kids [{' '.join(f'{pid} 0 R' for pid in page_ids)}] /Count {len(page_ids)} >>\nendobj\n".encode("latin-1"),
        b"3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    all_objects = header_objects + objects
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in all_objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(all_objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(all_objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
    )
    PDF_PATH.write_bytes(pdf)


def main():
    markdown = build_markdown()
    MD_PATH.write_text(markdown, encoding="utf-8")
    make_pdf(markdown_to_plain_lines(markdown))
    print(f"Generados: {MD_PATH.name} y {PDF_PATH.name}")


if __name__ == "__main__":
    main()
