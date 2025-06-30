from beanie import Document
from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId


class InstructionSet(Document):
    pass

class Instruction(Document):
    pass

class MasterInstructionSet(Document):
    pass