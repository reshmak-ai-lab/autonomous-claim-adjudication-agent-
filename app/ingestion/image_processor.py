from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image


class ImageProcessor:
    """
    Validate and inspect medical document images
    before OCR processing.
    """

    SUPPORTED_FORMATS = {
        "PNG",
        "JPEG",
        "JPG",
        "TIFF",
        "BMP",
    }

    def process(
        self,
        file_path: str | Path,
    ) -> dict[str, Any]:
        """
        Open and inspect an image.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {path}"
            )

        with Image.open(path) as image:
            image_format = image.format or ""

            if image_format.upper() not in self.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported image format: "
                    f"{image_format}"
                )

            return {
                "filename": path.name,
                "format": image_format,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
            }