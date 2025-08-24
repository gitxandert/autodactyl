from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import os, sqlite3

from api_helpers.helper_classes import ChatRoutes, ChatMsg, ApproveMsg
from api_helpers.helper_functions import coerce_model_json

from courses.database import init_db, get_all_courses, get_sections, get_lessons
import llm_operations.course_building.course_builder as course_builder

DB_PATH = os.environ.get("SQLITE_PATH", "app/courses/database/courses.sqlite")

app = FastAPI()

@app.on_event("startup")
def on_startup():
    print("Initializing database")
    try:
        init_db(DB_PATH)
    except Exception as e:
        import traceback
        traceback.print_exc()

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
def approve(payload: ApproveMsg):
    try:
        # Ensure DB dir exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
        result = course_builder.approve_course(session_id=payload.session_id, db_path=DB_PATH)
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# add user_id (wrapped in helper class)
@app.get("/api/list-courses")
def list_courses():
    try:
        with sqlite3.connect(DB_PATH) as con:
            courses = get_all_courses(con)
        return {"ok": True, "result": courses}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/list-sections")
def list_sections(course_id: int = Query(..., ge=1)):
    try:
        with sqlite3.connect(DB_PATH) as con:
            sections = get_sections(con, course_id)
        return {"ok": True, "result": sections}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/list-lessons")
def list_lessons(section_id: int = Query(..., ge=1)):
    try:
        with sqlite3.connect(DB_PATH) as con:
            lessons = get_lessons(con, section_id)
        return {"ok": True, "result": lessons}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
