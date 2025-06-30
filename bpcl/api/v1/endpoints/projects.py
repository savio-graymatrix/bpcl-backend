from fastapi.routing import APIRouter
from fastapi import HTTPException
from bpcl.db.data_models.Project import Project, CreateProject, UpdateProject

router = APIRouter(prefix="/projects")

# Create Project
@router.post("/", response_model=Project)
async def create_project(project: CreateProject):
    project = Project(**project.model_dump())
    await project.insert()
    return project


# Get Project By ID
@router.get("/{id}",response_model=Project)
async def get_project(id: str):
    project = await Project.get(id)
    if not project:
        raise HTTPException(status_code=404, detail="Bid not found")
    return project