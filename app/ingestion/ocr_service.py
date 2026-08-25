from __future__ import annotations

from pathlib import Path

import pytesseract
from PIL import Image


class OCRService:
    """
    OCR service for scanned medical documents.
    """

    def extract_text(
        self,
        image_path: str | Path,
    ) -> str:
        """
        Extract text from an image using Tesseract OCR.
        """

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {path}"
            )

        with Image.open(path) as image:
            text = pytesseract.image_to_string(
                image
            )

        return text.strip()