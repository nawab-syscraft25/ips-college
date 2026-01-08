"""
College context middleware for admin panel.
Automatically determines selected college from query params or session.
"""
from fastapi import Request
from sqlalchemy.orm import Session
from app.models.college import College


class CollegeContextMiddleware:
    """
    Middleware to set college context for admin requests.
    Stores selected college_id in request state and session.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Get college_id from query params or session
        college_id = request.query_params.get("college_id")
        
        if college_id:
            # Store in session for persistence
            request.session["selected_college_id"] = int(college_id)
        else:
            # Try to get from session
            college_id = request.session.get("selected_college_id")
        
        # Store in request state for use in route handlers
        if college_id:
            request.state.college_id = int(college_id)
        
        response = await call_next(request)
        return response


def get_selected_college_id(request: Request):
    """Extract selected college ID from request."""
    return getattr(request.state, "college_id", None)


def get_all_colleges_for_dropdown(db: Session, selected_college_id: int = None):
    """
    Get all colleges formatted for dropdown selection.
    Returns list with root colleges first, then children indented.
    """
    def format_college_list(college, depth=0):
        items = [{
            "id": college.id,
            "name": ("&nbsp;&nbsp;" * depth) + ("└─ " if depth > 0 else "") + college.name,
            "selected": college.id == selected_college_id if selected_college_id else False
        }]
        
        # Add children
        for child in college.children:
            items.extend(format_college_list(child, depth + 1))
        
        return items
    
    # Get root colleges
    root_colleges = db.query(College).filter(College.parent_id == None).all()
    
    result = []
    for college in root_colleges:
        result.extend(format_college_list(college))
    
    return result
