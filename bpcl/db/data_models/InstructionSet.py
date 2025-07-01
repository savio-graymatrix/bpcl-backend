from beanie import Document
from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime, timezone
from typing import Optional, List, Literal
from bson import ObjectId


class InstructionSet(Document):
    instruction_type: Literal["request_for_proposal","statement_of_work"]
    project_id: ObjectId
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId:str
        }
    )
    class Settings():
        name = "instruction_set"

class Instruction(Document):
    content: str
    instruction_set_id: ObjectId
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId:str
        }
    )
    class Settings():
        name = "instruction"

class MasterInstructionSet(Document):
    instruction_type: Literal["request_for_proposal","statement_of_work"]
    project_id: ObjectId
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId:str
        }
    )
    class Settings():
        name = "master_instruction_set"