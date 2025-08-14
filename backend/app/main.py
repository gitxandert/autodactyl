from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
import os, sqlite3

from api_helpers.helper_classes import CourseMsg, ApproveMsg
from api_helpers.helper_functions import coerce_model_json

from courses.database import init_db, get_all_courses
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
@app.post("/api/build-course")
def build_course(payload: CourseMsg):
    try:
        raw = course_builder.build_course(
            message=payload.message, session_id=payload.session_id
        )
        obj = coerce_model_json(raw)

        # If obj["draft"] is itself a JSON string, parse that too
        draft = obj.get("draft")
        if isinstance(draft, str):
            try:
                obj["draft"] = coerce_model_json(draft)
            except Exception:
                pass  # leave as-is if not valid
        
        course_builder.set_draft(obj["draft"])
        # Return a true JSON object, not a quoted string
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

# make this into POST later, with user_id (wrapped in helper class)
@app.get("/api/list-courses")
def list_courses():
    try:
        con = sqlite3.connect(DB_PATH)
        courses = get_all_courses(con)
        return JSONResponse({"ok": True, "result": courses})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
