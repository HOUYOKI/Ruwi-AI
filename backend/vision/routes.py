"""Multipart upload endpoint for constrained artifact identification."""

from collections.abc import Callable

from fastapi import APIRouter, File, HTTPException, UploadFile

from .identify import (
    VisionConfigurationError,
    VisionProviderError,
    VisionResponseError,
    identify_artifact,
)
from .schemas import IdentificationResponse

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024


def create_vision_router(
    artifacts_by_id: dict[int, dict],
    identifier: Callable[[bytes, str, dict[int, dict]], IdentificationResponse] = identify_artifact,
) -> APIRouter:
    router = APIRouter(tags=["vision"])

    @router.post("/identify", response_model=IdentificationResponse)
    async def identify(file: UploadFile | None = File(default=None)):
        if file is None:
            raise HTTPException(status_code=400, detail="An artifact image is required")
        if file.content_type not in SUPPORTED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail="Supported image types are JPEG, PNG, and WebP")
        image_bytes = await file.read(MAX_IMAGE_BYTES + 1)
        await file.close()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="The uploaded image is empty")
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="The uploaded image must be 8 MB or smaller")
        if not _has_expected_signature(image_bytes, file.content_type):
            raise HTTPException(status_code=400, detail="The uploaded file does not match its image type")
        try:
            return identifier(image_bytes, file.content_type, artifacts_by_id)
        except VisionConfigurationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except VisionResponseError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except VisionProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return router


def _has_expected_signature(content: bytes, mime_type: str) -> bool:
    if mime_type == "image/jpeg":
        return content.startswith(b"\xff\xd8\xff")
    if mime_type == "image/png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if mime_type == "image/webp":
        return len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP"
    return False
