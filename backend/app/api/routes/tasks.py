import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Project,
    # ProjectRole,
    # Project_User,
    Task,
    TaskCreate,
    TaskPublic,
    TasksPublic,
    TaskBase,
    # TaskUpdate,
    Message,
    User,
)

router = APIRouter(prefix="/project/{project_id}/tasks", tags=["tasks"])


@router.post("/", response_model=Task)
def create_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    task_in: TaskCreate,
) -> Any:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # project_user = session.exec(
    #     select(Project_User)
    #     .where(Project_User.project_id == project_id)
    #     .where(Project_User.user_id == current_user.id)
    #     .where(Project_User.role == ProjectRole.OWNER)
    # ).first()
    # verify_permissions(current_user, project_user)
    task = Task(
        name=task_in.name,
        description=task_in.description,
        status="pending",
        end_date="2023-05-01",
        project_id=project.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/", response_model=TasksPublic)
def read_tasks(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Get list.
    """
    count_statement = select(func.count()).select_from(Task)
    count = session.exec(count_statement).one()

    query = select(Task).offset(skip).limit(limit)
    projects = session.exec(query).all()
    return TasksPublic(data=projects, count=count)


@router.get("/{id}", response_model=Task)
def read_task_detail(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get
    """
    item = session.get(Task, id)
    if not item:
        raise HTTPException(status_code=404, detail="Projects not found")
    # if not current_user.is_superuser and (item.assigner_id != current_user.id):
    #     raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.put("/{task_id}", response_model=TaskPublic)
def update_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    task_in: Task,
) -> Any:
    # project = session.get(Project, project_id)
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")
    # project_user = session.exec(
    #     select(Project_User)
    #     .where(Project_User.project_id == project_id)
    #     .where(Project_User.user_id == current_user.id)
    # ).first()
    # verify_permissions(current_user, project_user)
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
    # project = session.get(Project, project_id)
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")
    # project_user = session.exec(
    #     select(Project_User)
    #     .where(Project_User.project_id == project_id)
    #     .where(Project_User.user_id == current_user.id)
    # ).first()
    # verify_permissions(current_user, project_user)
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
    # project = session.get(Project, project_id)
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")
    # project_user = session.exec(
    #     select(Project_User)
    #     .where(Project_User.project_id == project_id)
    #     .where(Project_User.user_id == current_user.id)
    # ).first()
    # if not project_user and not current_user.is_superuser:
    #     raise HTTPException(
    #         status_code=403, detail="Not authorized to update task in this project"
    #     )
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
    # project = session.get(Project, project_id)
    # if not project:
    #     raise HTTPException(status_code=404, detail="Project not found")
    # project_user = session.exec(
    #     select(Project_User)
    #     .where(Project_User.project_id == project_id)
    #     .where(Project_User.user_id == current_user.id)
    # ).first()
    # verify_permissions(current_user, project_user)
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


# def verify_permissions(current_user: CurrentUser, project_user: Project_User) -> None:
#     if not current_user.is_superuser and (
#         not project_user or project_user.role != ProjectRole.OWNER
#     ):
#         raise HTTPException(status_code=403, detail="Not enough permissions")
