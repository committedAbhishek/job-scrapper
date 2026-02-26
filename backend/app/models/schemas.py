from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List


class JobResponse(BaseModel):
    id: int
    company: str
    title: str
    location: Optional[str]
    url: str
    posted_at: datetime

    status: str
    applied_at: Optional[datetime]

    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedJobsResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[JobResponse]