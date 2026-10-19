
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.file_storage import save_invoice_file
from app.services.metadata_storage import create_document_metadata, list_documents, get_document


router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("", status_code=201)
async def upload_invoice(file: UploadFile = File(...)):
    file_info = await save_invoice_file(file)
    storage_path = Path(file_info["storage_path"])

    try:
        document = create_document_metadata(file_info)
    except Exception:
        # Avoid leaving an uploaded file without a metadata record.
        storage_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Upload failed because the document metadata could not be recorded.",
        )

    return {
        "message": "Invoice file uploaded successfully.",
        "file": document,
    }

@router.get("")
def get_invoices():
    documents = list_documents()

    return {
        "count": len(documents),
        "documents": documents,
    }

@router.get("/{invoice_id}/file")
def download_invoice_file(invoice_id: str):
    document = get_document(invoice_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    file_path = (
        Path(__file__).resolve().parents[3]
        / "storage"
        / "files"
        / document["stored_filename"]
    )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stored file not found.",
        )

    return FileResponse(
        path=file_path,
        media_type=document["content_type"],
        filename=document["original_filename"],
    )
