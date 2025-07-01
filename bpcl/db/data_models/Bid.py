from beanie import Document
from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from .File import File


class Bid(Document):
    project_id: str
    applicant_name: str
    # amount: float
    # gstin_no: str
    # pan_id: str
    #documents: List[ObjectId] = Field(default_factory=list)
    documents: File
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "bids"

    model_config = ConfigDict(
        json_encoders = {
            ObjectId: str
        },
        arbitrary_types_allowed=True,
    )


class CreateBid(BaseModel):
    project_id: str
    applicant_name: str
    # amount: float
    # gstin_no: str
    # pan_id: str
    #documents: List[str]
    documents: File

    model_config = ConfigDict(
        json_encoders = {
            ObjectId: str
        },
        arbitrary_types_allowed=True,
    )


class UpdateBid(BaseModel):
    applicant_name: Optional[str]
    # amount: Optional[float]
    # gstin_no: Optional[str]
    # pan_id: Optional[str]
    #documents: Optional[List[str]]
    documents: Optional[File]