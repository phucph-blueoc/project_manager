from enum import Enum
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
    ProjectCreate,
    Project_User,
    User,
    Users
    )

class ProjectRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"

router = APIRouter(prefix='/projects', tags=["projects"])

@router.get(
    "/",
    response_model=ProjectsList
)
def read_projects(session: SessionDep, current_user, skip: int = 0, limit: int = 100) -> Any:
    """
    Get list projects.
    """
    count_statement = select(func.count()).select_from(Project)
    count = session.exec(count_statement).one()
    
    query = select(Project).join(Project_User, Project_User.project_id == Project.id).where(Project_User.user_id == current_user.id).offset(skip).limit(limit)
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

@router.get("/{project_id}/members")
def get_project_users(project_id: uuid.UUID, session: SessionDep):
    stmt = (
        select(User.id, User.email, User.full_name, Project_User.role)
        .join(Project_User, Project_User.user_id == User.id)
        .where(Project_User.project_id == project_id)
    )
    users = session.exec(stmt).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found for this project")

    return [
        {"user_id": user.id, "name": user.full_name, "email": user.email, "role": user.role}
        for user in users
    ]

@router.delete("/{project_id}/members/{user_id}")
def delete_project_users(project_id: uuid.UUID, user_id: uuid.UUID, session: SessionDep):
    user = (
        select(Project_User)
        .where(Project_User.project_id == project_id, Project_User.user_id == user_id)
    )

    item = session.execute(user).scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Projects not found")
    session.delete(item)
    session.commit()
    return {"message": "User deleted"}

@router.post("/", response_model=Project)
def create_project(*, session:SessionDep, current_user: CurrentUser, project_in: ProjectCreate) -> Any:
    """
    Create project.
    """
    project = Project.model_validate(project_in, update={"owner_id": current_user.id})
    session.add(project)
    new_record = Project_User(project_id=project_in.id, user_id=current_user.id)
    session.add(new_record)

    session.commit()
    session.refresh(project)
    return project

@router.post("/{project_id}/add_member/{user_id}")
def add_user_to_project(project_id: uuid.UUID, user_id: uuid.UUID, session: SessionDep):
    stmt = select(Project_User).where(
        Project_User.project_id == project_id,
        Project_User.user_id == user_id,
    )
    existing_record = session.exec(stmt).all()
    if existing_record:
        raise HTTPException(status_code=400, detail="Record already exists")

    # Insert the new record
    new_record = Project_User(project_id=project_id, user_id=user_id)


    try:
        session.add(new_record)
        session.commit()
        return {"message": "User added to project successfully"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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

@router.post("/{project_id}/members", response_model=Message)
def add_member_to_project(
    project_id: uuid.UUID,
    member_data: Users,
    session: SessionDep,
    current_user: CurrentUser,
) -> Message:
    """
    Add a member to the project.
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    user = session.get(User, member_data.id)
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    existing_member = session.exec(
        select(Project_User).where(
            Project_User.project_id == project_id,
            Project_User.user_id == member_data.id,
        )
    ).first()
    if existing_member:
        raise HTTPException(
            status_code=400, detail="User is already a member of the project"
        )
    project_user = Project_User(
        project_id=project_id, user_id=member_data.id, role=ProjectRole.MEMBER
    )
    session.add(project_user)
    session.commit()
    return {"message": "User added to the project successfully"}
