from pydantic import BaseModel
from datetime import datetime


class JobResponse(BaseModel):
    id: int
    company: str
    title: str
    location: str | None
    url: str
    posted_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True