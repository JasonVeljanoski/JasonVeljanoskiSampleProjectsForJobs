from turtle import back
from .base import Base
from datetime import datetime

class Master(Base):
    updated: datetime = None
    source: str = None 
    system_id: str = None
    title: str = None
    description: str = None
    completion: str = None
    date_due: datetime = None
    supervisor: str = None
    employee: list[str] = None
    priority: str = None
    location: str = None
    confidential: bool = False 