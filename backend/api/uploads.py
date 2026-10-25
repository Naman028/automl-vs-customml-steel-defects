"""Shared upload validation at the HTTP boundary."""

import io
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from backend.core.config import SETTINGS

ALLOWED_IMAGE_MIME = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/bmp"}


async def load_validated_image(file: UploadFile) -> Image.Image:
    if file.content_type not in ALLOWED_IMAGE_MIME:
        raise HTTPException(
            status_code=415, detail=f"Unsupported content type: {file.content_type}"
        )
    content = await file.read(SETTINGS.max_upload_bytes + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    if len(content) > SETTINGS.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max allowed: {SETTINGS.max_upload_bytes} bytes",
        )
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
        with Image.open(io.BytesIO(content)) as image:
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise HTTPException(status_code=400, detail="Invalid image file") from error
