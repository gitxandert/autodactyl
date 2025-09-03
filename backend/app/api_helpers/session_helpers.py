from fastapi import Request, HTTPException
import uuid, bcrypt
import redis.asyncio as redis
import os

SESSION_COOKIE = "sid"
SESSION_TTL = 60 * 60 * 24

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

r = redis.from_url(REDIS_URL, decode_responses=True)

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def hash_password(pw: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw.encode("utf-8"), salt)
    return hashed.decode()

# --- sessions ---
async def create_session(user_id: str) -> str:
    sid = str(uuid.uuid4())
    key = f"session:{sid}"
    await r.hset(key, mapping={"user_id": user_id})
    await r.expire(key, SESSION_TTL)
    return sid

async def destroy_session(sid: str):
    await r.delete(f"session:{sid}")

async def get_session_user_id(request: Request) -> str | None:
    sid = request.cookies.get(SESSION_COOKIE)
    if not sid:
        return None
    user_id = await r.hget(f"session:{sid}", "user_id")
    if not user_id:
        return None
    # optional: sliding expiration
    await r.expire(f"session:{sid}", SESSION_TTL)
    return user_id

async def require_user_id(request: Request) -> str:
    uid = await get_session_user_id(request)
    if not uid:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return uid

