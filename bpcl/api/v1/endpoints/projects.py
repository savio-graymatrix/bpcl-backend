from fastapi.routing import APIRouter
from fastapi import HTTPException
from bpcl.db.data_models.Project import Project, CreateProject, UpdateProject
from bpcl.db.data_models.InstructionSet import InstructionSet, Instruction
from bpcl.langgraph.agents.instruction_agent import InstructionAgent
from traceback import format_exc
from bpcl import LOGGER
from fastapi import APIRouter, HTTPException, Query, Depends
from bpcl.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from typing import Optional

router = APIRouter(prefix="/projects",tags=["Projects"])

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


@router.get("/")
async def get_all_projects(
    pagination: CursorPaginationRequest = Depends(),
    created_at: Optional[str] = Query(None)
):
    query = {}
    query.update(parse_operator_filter("created_at", created_at))

    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Project.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Project.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Project.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Project](items=items, next_cursor=next_cursor)
