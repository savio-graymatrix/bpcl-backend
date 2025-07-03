from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Optional
from beanie import Document
from bson import ObjectId
from datetime import datetime, timezone


class Review(Document):
    type: Literal["caution", "warning", "error"]
    reason: str
    title: str
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
    id: str
    type: Literal["caution", "warning", "error"]
    reason: str
    title: str
    review_set_id: str
    status: Literal["pending", "resolved", "rejected"]


class ReviewSetResponse(BaseModel):
    application_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reviews: List[ReviewResponse]
    score: int
    feedback: str
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

class UpdateReview(BaseModel):
    id: Optional[str] = None
    type: Optional[Literal["caution", "warning", "error"]] = None
    reason: Optional[str] = None
    review_set_id: Optional[str] = None
    title: Optional[str] = None
    status: Optional[Literal["pending", "resolved", "rejected"]] = None
    model_config = ConfigDict(
        json_encoders = {
            ObjectId: str
        },
        arbitrary_types_allowed=True,
    )