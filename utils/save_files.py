import os
import uuid
from fastapi import HTTPException, UploadFile
import aiofiles

UPLOAD_DIR = "resources/"

async def save_file(file: UploadFile, folder: str = UPLOAD_DIR) -> str:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    os.makedirs(folder, exist_ok=True)
    ext = os.path.splitext(file.filename)[-1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(folder, filename)

    async with aiofiles.open(path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    await file.close()
    return path