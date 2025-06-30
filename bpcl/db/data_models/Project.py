from beanie import Document
from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId


class Project(Document):
    pass


class CreateProject(BaseModel):
    pass

class UpdateProject(BaseModel):
    pass