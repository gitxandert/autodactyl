from pydantic import BaseModel

class CourseMsg(BaseModel):
    message: str
    session_id: str

class ApproveMsg(BaseModel):
    session_id: str
