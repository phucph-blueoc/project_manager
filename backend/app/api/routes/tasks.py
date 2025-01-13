from enum import Enum
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    GetListTask,
    Project,
    Project_User,
    Task,
    TaskCreate,
    TaskPublic,
    TasksPublic,
    TaskBase,
    Message,
    User,
)


class ProjectRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"


router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


@router.post("/", response_model=Task)
def create_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    task_in: Task,
) -> Any:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_user = session.exec(
        select(Project_User)
        .where(Project_User.project_id == project_id)
        .where(Project_User.user_id == current_user.id)
        .where(Project_User.role == ProjectRole.OWNER)
    ).first()
    verify_permissions(current_user, project_user)
    task = Task(
        name=task_in.name,
        description=task_in.description,
        status=task_in.status,
        end_date=task_in.end_date,
        project_id=project.id,
        assigner_id=task_in.assigner_id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/", response_model=GetListTask)
def read_tasks(
    session: SessionDep, project_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get list of tasks
    """
    count_statement = (
        select(func.count()).select_from(Task).where(Task.project_id == project_id)
    )
    count = session.exec(count_statement).one()
    query = select(Task).where(Task.project_id == project_id).offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return GetListTask(data=tasks, count=count)


@router.get("/{id}", response_model=Task)
def read_task_detail(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get
    """
    item = session.get(Task, id)
    if not item:
        raise HTTPException(status_code=404, detail="Projects not found")
    return item


@router.put("/{task_id}", response_model=Task)
def update_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    task_in: Task,
) -> Any:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_user = session.exec(
        select(Project_User)
        .where(Project_User.project_id == project_id)
        .where(Project_User.user_id == current_user.id)
    ).first()
    verify_permissions(current_user, project_user)
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.name = task_in.name
    task.description = task_in.description
    task.status = task_in.status
    task.end_date = task_in.end_date
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", response_model=Message)
def delete_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
) -> Any:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_user = session.exec(
        select(Project_User)
        .where(Project_User.project_id == project_id)
        .where(Project_User.user_id == current_user.id)
    ).first()
    verify_permissions(current_user, project_user)
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return Message(message="Task deleted successfully")


@router.put("/{task_id}/status", response_model=Task)
def update_task_status(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    task_in: Task,
) -> Any:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_user = session.exec(
        select(Project_User)
        .where(Project_User.project_id == project_id)
        .where(Project_User.user_id == current_user.id)
    ).first()
    if not project_user and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to update task in this project"
        )
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = task_in.status
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.post("/{task_id}/assign", response_model=Task)
def assign_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    task_in: Task,
) -> Any:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_user = session.exec(
        select(Project_User)
        .where(Project_User.project_id == project_id)
        .where(Project_User.user_id == current_user.id)
    ).first()
    verify_permissions(current_user, project_user)
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    assignee = session.get(User, task_in.assigner_id)
    if not assignee:
        raise HTTPException(status_code=404, detail="User not found")
    task.assigner_id = task_in.assigner_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def verify_permissions(current_user: CurrentUser, project_user: Project_User) -> None:
    if not current_user.is_superuser and (
        not project_user or project_user.role != ProjectRole.OWNER
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")
