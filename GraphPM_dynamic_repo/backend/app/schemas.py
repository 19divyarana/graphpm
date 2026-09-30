from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class ProjectIn(BaseModel):
    project_id: str
    name: str
    manager: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "ACTIVE"

class DeveloperIn(BaseModel):
    developer_id: str
    name: str
    role: str = "Developer"
    capacity_hours_per_week: float = 40

class TaskIn(BaseModel):
    task_id: str
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

class DependencyIn(BaseModel):
    source_task_id: str
    target_task_id: str
    type: str = "DEPENDS_ON"

class DefectIn(BaseModel):
    defect_id: str
    task_id: str
    severity: str = "MEDIUM"
    status: str = "OPEN"
    created_at: Optional[date] = None
    resolved_at: Optional[date] = None
