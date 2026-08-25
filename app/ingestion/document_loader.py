from __future__ import annotations

from pathlib import Path
from typing import Any

from app.ingestion.pdf_parser import PDFParser
from app.ingestion.document_classifier import DocumentClassifier


class DocumentLoader:
    """
    Loads claim documents and routes them to the
    appropriate parser.
    """

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".pdf",
        ".json",
        ".csv",
        ".png",
        ".jpg",
        ".jpeg",
    }

    def __init__(self) -> None:
        self.pdf_parser = PDFParser()
        self.classifier = DocumentClassifier()

    def load(self, file_path: str | Path) -> dict[str, Any]:
        """
        Load a document from disk.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported document type: {extension}"
            )

        document_type = self.classifier.classify(
            path
        )

        if extension == ".pdf":
            text = self.pdf_parser.parse(path)

        elif extension == ".txt":
            text = path.read_text(
                encoding="utf-8"
            )

        elif extension == ".json":
            text = path.read_text(
                encoding="utf-8"
            )

        elif extension == ".csv":
            text = path.read_text(
                encoding="utf-8"
            )

        else:
            text = ""

        return {
            "filename": path.name,
            "file_path": str(path),
            "extension": extension,
            "document_type": document_type,
            "text": text,
            "text_length": len(text),
        }