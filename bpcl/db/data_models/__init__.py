from .Bid import Bid, CreateBid, UpdateBid
from .File import File
from .InstructionSet import InstructionSet, Instruction, MasterInstructionSet
from .Project import Project
from .Review import Review, ReviewSet

DOCUMENT_MODELS = [
    Bid,
    ReviewSet,
    Review,
    Instruction,
    InstructionSet,
    MasterInstructionSet,
    File,
]
