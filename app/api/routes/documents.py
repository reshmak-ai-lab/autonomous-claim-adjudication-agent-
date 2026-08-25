from fastapi import APIRouter, File, HTTPException, UploadFile

from config.settings import settings

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".csv",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
) -> dict:
    """
    Upload a medical/claim document.

    Actual document processing should be delegated to
    the ingestion pipeline.
    """

    filename = file.filename or ""

    extension = ""

    if "." in filename:
        extension = "." + filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Allowed types: {sorted(ALLOWED_EXTENSIONS)}"
            ),
        )

    contents = await file.read()

    max_size = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=413,
            detail=(
                f"Document exceeds maximum size of "
                f"{settings.MAX_DOCUMENT_SIZE_MB} MB."
            ),
        )

    return {
        "status": "accepted",
        "filename": filename,
        "size_bytes": len(contents),
        "message": "Document accepted for processing.",
    }


@router.get("/{document_id}")
def get_document(document_id: str) -> dict:
    """
    Retrieve document processing status.
    """

    return {
        "document_id": document_id,
        "status": "processed",
    }