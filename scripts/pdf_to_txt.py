"""Convierte un PDF a TXT usando pypdf.

Uso:
    python scripts/pdf_to_txt.py ruta/al/archivo.pdf
    python scripts/pdf_to_txt.py ruta/al/archivo.pdf -o ruta/reflexiones.txt
    python scripts/pdf_to_txt.py ruta/al/archivo.pdf --encoding utf-8 --force

Si no se indica -o, el .txt se genera junto al PDF con el mismo nombre
(ej. ``documento.pdf`` -> ``documento.txt``).
"""

import argparse
import sys
from pathlib import Path

from pypdf import PdfReader


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convierte un PDF a TXT usando pypdf.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("pdf", type=Path, help="Ruta del archivo PDF a convertir")
    parser.add_argument("-o", "--output", type=Path, default=None,
                          help="Ruta del TXT de salida (por defecto: mismo nombre que el PDF)")
    parser.add_argument("--encoding", default="utf-8", help="Codificacion del TXT de salida")
    parser.add_argument("--force", action="store_true",
                          help="Sobrescribe el TXT si ya existe")
    parser.add_argument("--max-pages", type=int, default=None,
                          help="Limita el numero de paginas a procesar (por defecto: todas)")
    parser.add_argument("--include-page-separator", action="store_true",
                          help="Inserta cabecera de pagina (--- Pagina N ---) antes de cada pagina")
    return parser.parse_args(argv)


def extract_text(pdf_path: Path, max_pages: int | None = None) -> str:
    reader = PdfReader(str(pdf_path))
    total = len(reader.pages) if max_pages is None else min(len(reader.pages), max_pages)
    pages = []
    for index in range(total):
        page = reader.pages[index]
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(text.strip())
    return "\n".join(pages) + ("\n" if pages else "")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    pdf_path: Path = args.pdf
    if not pdf_path.exists():
        print(f"Error: no existe el archivo '{pdf_path}'", file=sys.stderr)
        return 1
    if pdf_path.suffix.lower() != ".pdf":
        print(f"Error: '{pdf_path}' no tiene extension .pdf", file=sys.stderr)
        return 1

    output_path: Path = args.output if args.output is not None else pdf_path.with_suffix(".txt")
    if output_path.exists() and not args.force and args.output is not None:
        print(f"Error: ya existe '{output_path}'. Usa --force para sobrescribir.", file=sys.stderr)
        return 1

    try:
        text = extract_text(pdf_path, max_pages=args.max_pages)
        if not text.strip():
            print(f"Aviso: no se extrajo texto de '{pdf_path}' (puede ser un PDF escaneado).", file=sys.stderr)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding=args.encoding)
    except Exception as error:
        print(f"Error: no se pudo convertir '{pdf_path}' a TXT: {error}", file=sys.stderr)
        return 1

    print(f"PDF convertido a TXT: {output_path} ({output_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
