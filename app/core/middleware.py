from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.models.college import College
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

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
            try:
                college = db.query(College).filter(
                    College.subdomain == subdomain,
                    College.is_active == True
                ).first()
            except Exception as e:
                logger.error(f"Error resolving college by subdomain: {e}")
                college = None

        request.state.college = college
        request.state.selected_college_id = int(college_id) if college_id else None
        
        # Pre-fetch colleges for dropdown in admin templates
        if "/admin" in request.url.path:
            try:
                all_colleges = db.query(College).filter(College.parent_id == None).all()
                request.state.colleges_for_dropdown = all_colleges
            except Exception as e:
                logger.error(f"Error fetching colleges for dropdown: {e}")
                request.state.colleges_for_dropdown = []
        
        try:
            response = await call_next(request)
        finally:
            # Safely close the database session
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")
                # Dispose of the session if close fails
                try:
                    db.dispose()
                except:
                    pass
        
        return response

