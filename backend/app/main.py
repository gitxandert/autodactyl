from fastapi import FastAPI, Depends, Query, Request, Response, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from psycopg import Connection
import uuid, bcrypt
import os

import api_helpers.session_helpers as session
from api_helpers.helper_classes import ChatRoutes, ChatMsg, ApproveMsg, LogIn
from api_helpers.helper_functions import coerce_model_json

import courses.database as db
import llm_operations.course_building.course_builder as course_builder

SESSION_COOKIE = "sid"
SESSION_TTL = 60 * 60 * 24
SECURE_COOKIES = False #SET TO TRUE FOR PROD
ALLOWED_ORIGINS = [
    "http://localhost:8080"
] #SET TO DOMAIN NAME FOR PROD

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    try:
        db.init_db()
    except Exception as e:
        import traceback
        traceback.print_exc()

def get_conn():
    con = db.open_db()
    try:
        yield con
    finally:
        con.close()

@app.get("/healthz")
def healthz():
    return PlainTextResponse("ok")

# ---- Route ----

@app.post("/api/login")
async def login(data: LogIn, response: Response, con: Connection = Depends(get_conn)):
    user = db.get_user_by_username(con, data.username)
    if not user or not session.verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    sid = await session.create_session(user["id"])
    response.set_cookie(
        key=SESSION_COOKIE,
        value=sid,
        max_age=SESSION_TTL,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        path="/",
    )
    return {"ok": True}

@app.post("/api/logout")
async def logout(request: Request, response: Response):
    sid = request.cookies.get(SESSION_COOKIE)
    if sid:
        await session.destroy_session(sid)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}

@app.get("/api/me")
async def me(user_id: str = Depends(session.require_user_id), con: Connection = Depends(get_conn)):
    user = db.get_user_by_id(con, user_id)
    return {"ok": True, "result": user}; 

@app.post("/api/register")
def register(data: LogIn, con: Connection = Depends(get_conn)):
    exists = db.get_user_by_username(con, data.username)
    print(f"{exists}")
    if exists:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed = session.hash_password(data.password)
    db.create_user(con, data.username, hashed)
    return {"ok": True}

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
def approve(payload: ApproveMsg, con: Connection = Depends(get_conn), user_id: int = Depends(session.get_session_user_id)):
    try:
        result = course_builder.approve_course(con, session_id=payload.session_id, user_id=user_id)
        return JSONResponse({"ok": True, "result": result})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# add user_id (wrapped in helper class)
@app.get("/api/list-courses")
def list_courses(con: Connection = Depends(get_conn), user_id: int = Depends(session.get_session_user_id)):
    try:
        courses = db.get_all_courses(con, user_id)
        return {"ok": True, "result": courses}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/list-sections")
def list_sections(course_id: int = Query(..., ge=1), con: Connection = Depends(get_conn)):
    try:
        sections = db.get_sections(con, course_id)
        return {"ok": True, "result": sections}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/list-lessons")
def list_lessons(section_id: int = Query(..., ge=1), con: Connection = Depends(get_conn)):
    try:
        lessons = db.get_lessons(con, section_id)
        return {"ok": True, "result": lessons}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/list-exercises")
def list_exercises(lesson_id: Query(..., ge=1), con: Connection = Depends(get_conn)):
    try:
        exercises = db.get_exercises(con, lesson_id)
        return {"ok": True, "result": exercises}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.get("/api/get-exercise")
def get_exercise(ex_id: int = Query(..., ge=1), con: Connection = Depends(get_conn)):
    try:
        exercise = db.get_exercise(con, ex_id)
        return {"ok": True, "result": exercise}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
