from beanie import init_beanie
from bpcl.db.data_models import DOCUMENT_MODELS
from motor.motor_asyncio import AsyncIOMotorClient
from bpcl import LOGGER,SETTINGS


class MongoDatabase:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None

    async def connect(self):
        self.client = AsyncIOMotorClient(SETTINGS.MONGO_URI)
        await init_beanie(
            database=self.client[SETTINGS.DB_NAME],
            document_models=DOCUMENT_MODELS,
        )
        LOGGER.info("MongoDB connection initialized")

    async def disconnect(self):
        if self.client:
            self.client.close()
            LOGGER.info("MongoDB connection closed")


MONGO_STORE = MongoDatabase()