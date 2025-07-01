from beanie import Document
from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from .File import File


class Project(Document):
    name : str
    domain: str
    rf_proposal: File
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId:str
        }
    )
    class Settings():
        name = "project"


class CreateProject(BaseModel):
    name : str
    domain: str
    rf_proposal: File

class UpdateProject(BaseModel):
    name : Optional[str]
    domain: Optional[str]
    rf_proposal: Optional[File]