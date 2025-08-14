from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
import os, json, re, sqlite3

from courses.database import init_db
import llm_operations.course_building.course_builder as course_builder

DB_PATH = os.environ.get("SQLITE_PATH", "app/courses/database/courses.sqlite")

app = FastAPI()

class CourseMsg(BaseModel):
    message: str
    session_id: str

class ApproveMsg(BaseModel):
    session_id: str

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

def _strip_code_fences(s: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", s.strip(), flags=re.IGNORECASE)

def coerce_model_json(x):
    # Already a dict? good.
    if isinstance(x, dict):
        return x
    # Model object with .content
    if hasattr(x, "content"):
        x = x.content
    # Bytes -> str
    if isinstance(x, (bytes, bytearray)):
        x = x.decode("utf-8", errors="replace")
    # If not a string by now, stringify (last resort)
    if not isinstance(x, str):
        x = str(x)
    # Try raw parse
    try:
        return json.loads(x)
    except Exception:
        pass
    # Try without code fences
    try:
        return json.loads(_strip_code_fences(x))
    except Exception:
        pass
    # If the model returned a JSON object as a *string* inside quotes,
    # attempt one more pass (e.g., "\"{...}\"")
    try:
        inner = json.loads(x)
        if isinstance(inner, str):
            return json.loads(_strip_code_fences(inner))
        return inner
    except Exception:
        raise ValueError("Model did not return valid JSON")

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
        # If using Flask instead of FastAPI:
        # from flask import jsonify
        # return jsonify({"ok": True, "result": obj})
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

@app.post("/api/list-courses")
def list_courses():
    # will eventually need to accept a payload: user_id
    pass
