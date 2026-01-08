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
        
        # Get college_id from query params or session
        college_id = request.query_params.get("college_id")
        if college_id:
            try:
                request.session["selected_college_id"] = int(college_id)
            except RuntimeError:
                # Session not available yet (might be during non-admin request)
                pass
        else:
            # Try to get from session
            try:
                college_id = request.session.get("selected_college_id")
            except RuntimeError:
                college_id = None

        # Subdomain-based college resolution (for frontend)
        if subdomain not in ["www", "ipsacademy", "localhost"]:
            college = db.query(College).filter(
                College.subdomain == subdomain,
                College.is_active == True
            ).first()

        request.state.college = college
        request.state.selected_college_id = int(college_id) if college_id else None
        
        # Pre-fetch colleges for dropdown in admin templates
        if "/admin" in request.url.path:
            all_colleges = db.query(College).filter(College.parent_id == None).all()
            request.state.colleges_for_dropdown = all_colleges
        
        response = await call_next(request)
        db.close()
        return response

