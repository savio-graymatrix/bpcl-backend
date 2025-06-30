from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from bpcl.api.router import router as api_router
from bpcl.db.stores.MongoStore import MONGO_STORE

@asynccontextmanager
async def lifespan(app: FastAPI):
    await MONGO_STORE.connect()
    yield
    await MONGO_STORE.disconnect()



app = FastAPI(lifespan=lifespan)
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],
    )
app.include_router(api_router)

