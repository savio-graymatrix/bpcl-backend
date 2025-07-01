from .endpoints.bids import router as bids_router
from .endpoints.chat_stream import router as chat_stream_router
from .endpoints.parse_review import router as parse_review_router
from .endpoints.projects import router as projects_router
from .endpoints.file_upload import router as file_upload_router
from fastapi.routing import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(bids_router)
router.include_router(projects_router)
router.include_router(parse_review_router)
router.include_router(chat_stream_router)
router.include_router(file_upload_router)