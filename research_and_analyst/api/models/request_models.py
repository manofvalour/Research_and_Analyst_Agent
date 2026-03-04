from pydantic import BaseModel, field

class ReportRequest(BaseModel):
    topic:str = field(..., description = "topic for Report generation")
    max_analysts: int=Field(3, description="Number of analyst personas to create")

class FeedBackequest(BaseModel):
    thread_id:str
    feedback:str=""

from pydantic import BaseModel, Field
class LoginRequest(BaseModel):
    username: str = field(..., description="Username for login")
    password: str = field(..., description="password for login")

class SignupRequest(BaseModel):
    username: str= field(..., description="New username for signup")
    password: str = field(..., description="password for signup")

class ReportRequest(BaseModel):
    topic: str = field(..., description="Topic for report generation")
    feedback:str | None = Field(None, description="optional feedback from analyst")

