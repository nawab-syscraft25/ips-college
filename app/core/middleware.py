from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.models.college import College
from app.core.database import SessionLocal

class CollegeResolverMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        subdomain = host.split(".")[0]

        db = SessionLocal()
        college = None

        if subdomain not in ["www", "ipsacademy", "localhost"]:
            college = db.query(College).filter(
                College.subdomain == subdomain,
                College.is_active == True
            ).first()

        request.state.college = college
        response = await call_next(request)
        db.close()
        return response
