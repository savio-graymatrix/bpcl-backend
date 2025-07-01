from fastapi.routing import APIRouter
from fastapi import HTTPException
from bpcl.db.data_models.Project import Project, CreateProject, UpdateProject
from bpcl.db.data_models.InstructionSet import InstructionSet, Instruction
from bpcl.langgraph.agents.instruction_agent import InstructionAgent
from traceback import format_exc
from bpcl import LOGGER

router = APIRouter(prefix="/projects")

ALLOWED_MIME_TYPES = {"application/pdf"}


# Create Project
@router.post("/")
async def create_project(project: CreateProject):
    try:
        project = Project(**project.model_dump())
        if project.rf_proposal.content_type not in ALLOWED_MIME_TYPES:
            return HTTPException(400, "Invalid File Type")
        await project.insert()
        config = {"configurable": {"thread_id": 1, "project_id": project.id}}
        result = await InstructionAgent.instruction_agent({"messages": []}, config=config)
        instruction_set = InstructionSet(
            instruction_type="request_for_proposal", project_id=project.id
        )
        await instruction_set.insert()
        for instruction in result.instruction_set:
            instruction = Instruction(
                content=instruction.instruction, instruction_set_id=instruction_set.id
            )
            await instruction.insert()

        # print(result)
        return project
    except Exception as e:
        LOGGER.debug(format_exc())
        return HTTPException(status_code=500, detail="Internal Server Error")


# Get Project By ID
@router.get("/{id}")
async def get_project(id: str):
    project = await Project.get(id)
    if not project:
        raise HTTPException(status_code=404, detail="Bid not found")
    return project
