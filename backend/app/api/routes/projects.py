import uuid
from typing import Any
 
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import (
    SessionDep,
    CurrentUser
)
from app.models import(
    Message,
    ProjectsList,
    ProjectList,
    Project,
    ProjectCreate
    )

router = APIRouter(prefix='/projects', tags=["projects"])

@router.get(
    "/",
    response_model=ProjectsList
)
def read_projects(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Get list projects.
    """
    count_statement = select(func.count()).select_from(Project)
    count = session.exec(count_statement).one()
    
    query = select(Project).offset(skip).limit(limit)
    projects = session.exec(query).all()
    return ProjectsList(data=projects, count = count)

@router.get("/{id}", response_model=Project)
def read_project(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get project by ID.
    """
    item = session.get(Project, id)
    if not item:
        raise HTTPException(status_code=404, detail="Projects not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item

@router.post("/", response_model=Project)
def create_project(*, session:SessionDep, current_user: CurrentUser, project_in: ProjectCreate) -> Any:
    """
    Create project.
    """
    project = Project.model_validate(project_in, update={"owner_id": current_user.id})
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.put("/{id}", response_model=Project)
def update_project(*, session: SessionDep, current_user: CurrentUser, id: uuid.UUID, project_in: ProjectCreate) -> Any:
    """
    Update project.
    """
    project = session.get(Project, id)
    if not project:
        raise HTTPException(status_code=404, detail="Projects not found")
    if not current_user.is_superuser and (project.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = project_in.model_dump(exclude_unset=True)
    project.sqlmodel_update(update_dict)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/{id}")
def delete_project(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Message:
    """
    Delete project.
    """
    item = session.get(Project, id)
    if not item:
        raise HTTPException(status_code=404, detail="Projects not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return {"message": "Project deleted"}

@router.get("/member")
def get_member(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Get member.
    """
    count_statement = select(func.count()).select_from(Project)
    count = session.exec(count_statement).one()