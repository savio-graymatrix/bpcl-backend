from fastapi import APIRouter, UploadFile, File as FastAPIFile, HTTPException
from uuid import uuid4
from bpcl.db.data_models.File import File
from bpcl.services.upload_to_s3 import upload_to_s3  

router = APIRouter(tags=["File Upload"])

ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "application/pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/upload", response_model=File)
async def upload_file(file: UploadFile = FastAPIFile(...)):
    content = await file.read()

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid4().hex}.{ext}"

    try:
        public_url = upload_to_s3(content, unique_filename, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    file_doc = File(
        name=file.filename,
        url=public_url,
        content_type=file.content_type,
        size=len(content),
    )
    await file_doc.insert()

    return file_doc