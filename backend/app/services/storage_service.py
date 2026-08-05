from pathlib import Path
from uuid import uuid4
from PIL import Image
from fastapi import UploadFile, HTTPException
from app.core.config import settings
class StorageService:
    image_types={"image/jpeg":".jpg","image/png":".png","image/webp":".webp"}
    doc_types={"application/pdf":".pdf","text/plain":".txt","text/markdown":".md"}
    @classmethod
    async def save_image(cls,file:UploadFile):
        if file.content_type not in cls.image_types: raise HTTPException(415,detail={"code":"UNSUPPORTED_IMAGE","message":"JPEG, PNG, or WebP required"})
        data=await file.read()
        if len(data)>settings.max_image_mb*1024*1024: raise HTTPException(413,detail={"code":"IMAGE_TOO_LARGE","message":"Image exceeds configured limit"})
        base=Path(settings.local_storage_dir)/"images"; base.mkdir(parents=True,exist_ok=True)
        path=base/f"{uuid4().hex}{cls.image_types[file.content_type]}"; path.write_bytes(data)
        try:
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                width,height=im.size
                if width<64 or height<64 or width>12000 or height>12000: raise ValueError("Invalid dimensions")
                im.thumbnail((2400,2400)); im.save(path,optimize=True)
        except Exception:
            path.unlink(missing_ok=True); raise HTTPException(422,detail={"code":"INVALID_IMAGE","message":"The file is not a valid supported image"})
        return path,file.content_type,len(data),width,height
