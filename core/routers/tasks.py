from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.database import get_db
from models.users import UserModel
from models.tasks import TaskModel
from auth.jwt_cookie_auth import get_authenticated_user
from messages.tasks import Messages
from schemas.tasks import TaskResponseSchema, TaskUpdateSchema, TaskCreateSchema
from utils.paginations import paginate, PaginatedResponse
from typing import Optional
from uuid import UUID


router = APIRouter(tags=["tasks"], prefix="/api/v1")


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    request: TaskCreateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    task = TaskModel(
        user_id = user.id,
        title = request.title,
        description = request.description,
        priority = request.priority.value,
        due_date = request.due_date
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": Messages.task_created_successfully})



@router.get("/tasks", response_model=PaginatedResponse[TaskResponseSchema], status_code=status.HTTP_200_OK)
def get_tasks(
    request: Request,
    search: Optional[str] = Query(None, description="Search in title and description"),
    ordering: str = Query("created_date", description="Ordering field, prefix with '-' for desc"),
    is_completed: Optional[bool] = Query( None, description="Filter by completion status" ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    query = ( db.query(TaskModel) .filter(TaskModel.user_id == user.id) )

    # Search
    if search: 
        search_term = f"%{search}%" 
        query = query.filter( TaskModel.title.ilike(search_term) |
                              TaskModel.description.ilike(search_term) )

    if is_completed is not None:
        query = query.filter(TaskModel.is_completed == is_completed)

    # Ordering
    ordering_fields = {
        "created_date": TaskModel.created_date, 
        "updated_date": TaskModel.updated_date, 
        "title": TaskModel.title, 
        "due_date": TaskModel.due_date, 
        "priority": TaskModel.priority, 
        } 

    descending = ordering.startswith("-") 
    ordering_field = ordering.lstrip("-") 

    if ordering_field not in ordering_fields: 
        ordering_field = "created_date" 

    order_column = ordering_fields[ordering_field] 

    if descending: 
        query = query.order_by(order_column.desc()) 
    else: 
        query = query.order_by(order_column.asc()) 


    return paginate( 
        query=query, 
        schema=TaskResponseSchema, 
        request=request, 
        page=page, 
        page_size=page_size, 
        )
    


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema, status_code=status.HTTP_200_OK)
def retrieve_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    task = db.query(TaskModel).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.task_not_found)
    return task


@router.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def update_task(
    task_id: UUID,
    request: TaskUpdateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user.id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.task_not_found)

    update_data = request.model_dump(exclude_unset=True)

    if "priority" in update_data: 
        update_data["priority"] = update_data["priority"].value

    # Update only fields provided in request
    for field, value in update_data.items(): 
        setattr(task, field, value)

    db.commit() 
    db.refresh(task)

    return {"detail": Messages.task_updated_successfully}


@router.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user),
):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user.id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Messages.task_not_found)

    db.delete(task)
    db.commit() 

    return {"detail": Messages.task_removed_successfully}