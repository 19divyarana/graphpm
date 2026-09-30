from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field

class Project(SQLModel, table=True):
    project_id: str = Field(primary_key=True)
    name: str
    manager: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "ACTIVE"

class Developer(SQLModel, table=True):
    developer_id: str = Field(primary_key=True)
    name: str
    role: str = "Developer"
    capacity_hours_per_week: float = 40

class Task(SQLModel, table=True):
    task_id: str = Field(primary_key=True)
    project_id: str
    title: str
    status: str = "TODO"
    priority: str = "MEDIUM"
    developer_id: Optional[str] = None
    module_id: Optional[str] = None
    created_at: Optional[datetime] = None
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    story_points: float = 0
    estimated_hours: float = 0
    actual_hours: float = 0
    defect_count: int = 0
    risk_label: Optional[int] = None

class Dependency(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_task_id: str
    target_task_id: str
    type: str = "DEPENDS_ON"

class Defect(SQLModel, table=True):
    defect_id: str = Field(primary_key=True)
    task_id: str
    severity: str = "MEDIUM"
    status: str = "OPEN"
    created_at: Optional[date] = None
    resolved_at: Optional[date] = None
