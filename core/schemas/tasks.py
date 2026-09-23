from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from models.tasks import PriorityEnum
import re
from uuid import UUID

class TaskCreateSchema(BaseModel):
    title: Optional[str] = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    priority: PriorityEnum = PriorityEnum.MEDIUM.value
    due_date: Optional[datetime] = None


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None



class TaskResponseSchema(BaseModel): 
    model_config = ConfigDict(from_attributes=True) 

    id: UUID
    title: str 
    description: Optional[str] 
    is_completed: bool 
    priority: PriorityEnum 
    due_date: Optional[datetime]
    created_date: datetime 
    updated_date: datetime
