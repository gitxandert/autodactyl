from pydantic import BaseModel
import llm_operations.course_building.course_builder as course_builder
# import llm_operations.course_learning.course_teacher as course_teacher

class ChatRoutes:
    functions = {
        "build": course_builder.build_course
        # "learn": course_teacher.iterate_lesson
    }

class ChatMsg(BaseModel):
    purpose: str
    message: str
    session_id: str

class ApproveMsg(BaseModel):
    session_id: str
