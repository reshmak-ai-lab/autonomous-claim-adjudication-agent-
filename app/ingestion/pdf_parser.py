from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class PDFParser:
    """
    Extract text from PDF documents.
    """

    def parse(
        self,
        file_path: str | Path,
    ) -> str:
        """
        Extract text from all PDF pages.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {path}"
            )

        reader = PdfReader(str(path))

        pages: list[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text.strip())

        return "\n\n".join(pages)