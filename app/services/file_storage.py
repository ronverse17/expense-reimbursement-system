
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile


STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "files"

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


async def save_invoice_file(file: UploadFile) -> dict:
    original_filename = file.filename or "unnamed"
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Upload a PDF, JPG, JPEG, or PNG.",
        )

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Generate our own filename; never use the supplied filename as a path.
    stored_filename = f"{uuid4().hex}{extension}"
    destination = STORAGE_DIR / stored_filename

    total_size = 0
    first_bytes = b""

    try:
        with destination.open("wb") as output:
            while True:
                chunk = await file.read(1024 * 1024)  # Read 1 MB at a time.

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File is too large. Maximum size is 10 MB.",
                    )

                if len(first_bytes) < 8:
                    first_bytes += chunk[: 8 - len(first_bytes)]

                output.write(chunk)

        # Check the file's signature, not just its extension.
        valid_signatures = {
            ".pdf": first_bytes.startswith(b"%PDF-"),
            ".jpg": first_bytes.startswith(b"\xff\xd8\xff"),
            ".jpeg": first_bytes.startswith(b"\xff\xd8\xff"),
            ".png": first_bytes.startswith(b"\x89PNG\r\n\x1a\n"),
        }

        if total_size == 0 or not valid_signatures[extension]:
            raise HTTPException(
                status_code=400,
                detail="File contents do not match the file extension, or the file is empty.",
            )

        return {
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "content_type": ALLOWED_EXTENSIONS[extension],
            "size_bytes": total_size,
            "storage_path": str(destination),
        }

    except Exception:
        # Do not leave a partial file behind if saving or validation fails.
        destination.unlink(missing_ok=True)
        raise

    finally:
        await file.close()
