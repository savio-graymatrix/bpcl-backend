from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal
from beanie import Document
from bson import ObjectId
from datetime import datetime, timezone


class Review(Document):
    type: Literal["caution", "warning", "error"]
    reason: str
    review_set_id: ObjectId
    status: Literal["pending", "resolved", "rejected"]

    class Settings:
        name = "review"

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders = {
            ObjectId: str
        },
    )


class ReviewSet(Document):
    application_id: ObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    score: int
    feedback: str
    class Settings:
        name = "review-set"
    model_config = ConfigDict(
        json_encoders = {
            ObjectId: str
        },
        arbitrary_types_allowed=True,
    )


class ReviewResponse(BaseModel):
    type: Literal["caution", "warning", "error"]
    reason: str


class ReviewSetResponse(BaseModel):
    application_id: ObjectId
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviews: List[ReviewResponse]
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )