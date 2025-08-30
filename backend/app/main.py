from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from psycopg import Connection
import os

from api_helpers.helper_classes import ChatRoutes, ChatMsg, ApproveMsg
from api_helpers.helper_functions import coerce_model_json

from courses.database import init_db, open_db, get_all_courses, get_sections, get_lessons
import llm_operations.course_building.course_builder as course_builder

app = FastAPI()

@app.on_event("startup")
def on_startup():
    try:
        init_db()
    except Exception as e:
        import traceback
        traceback.print_exc()

def get_conn():
    con = open_db()
    try:
        yield con
    finally:
        con.close()

@app.get("/healthz")
def healthz():
    return PlainTextResponse("ok")

# ---- Route ----
@app.post("/api/chat")
def chat(payload: ChatMsg):
    func = ChatRoutes.functions.get(payload.purpose)
    try:
        raw = func(message=payload.message, session_id=payload.session_id)
        if not func:
            raise HTTPException(status_code=400, detail=f"Unknown purpose '{payload.purpose}'")
        
        obj = coerce_model_json(raw)

        # If obj["draft"] exists and is itself a JSON string, parse that too
        if isinstance(obj, dict) and "draft" in obj:
            draft = obj.get("draft")
            if isinstance(draft, str):
                try:
                    obj["draft"] = coerce_model_json(draft)
                except Exception:
                    pass  # leave as-is if not valid
            course_builder.set_draft(obj["draft"])
        return JSONResponse({"ok": True, "result": obj})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/api/approve")
def approve(payload: ApproveMsg, con: Connection = Depends(get_conn)):
    try:
        result = course_builder.approve_course(con, session_id=payload.session_id)
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# add user_id (wrapped in helper class)
@app.get("/api/list-courses")
def list_courses(con: Connection = Depends(get_conn)):
    try:
        courses = get_all_courses(con)
        return {"ok": True, "result": courses}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/list-sections")
def list_sections(course_id: int = Query(..., ge=1), con: Connection = Depends(get_conn)):
    try:
        sections = get_sections(con, course_id)
        return {"ok": True, "result": sections}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/list-lessons")
def list_lessons(section_id: int = Query(..., ge=1), con: Connection = Depends(get_conn)):
    try:
        lessons = get_lessons(con, section_id)
        return {"ok": True, "result": lessons}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
