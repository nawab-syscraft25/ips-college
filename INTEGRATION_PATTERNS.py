"""
Quick Reference: College Context Integration Pattern

Use this as a template when updating your admin.py routes.
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from app.core.database import get_db
from app.models.college import College
from app.schemas.schema import Course, Page, PageSection, SEOMeta
from app.utils.college_context import (
    get_college_pages, get_college_courses, create_standard_pages_for_college
)

router = APIRouter()
templates_dir = Path(__file__).resolve().parents[3] / "templet"
templates = Jinja2Templates(directory=str(templates_dir))


# ============================================================================
# PATTERN 1: GET SELECTED COLLEGE
# ============================================================================
def _get_selected_college(request: Request, db: Session):
    """Helper to extract selected college from request"""
    # Try request state first (set by middleware)
    college_id = getattr(request.state, "selected_college_id", None)
    
    # Fall back to session
    if not college_id:
        college_id = request.session.get("selected_college_id")
    
    if not college_id:
        return None
    
    return db.query(College).filter(College.id == college_id).first()


# ============================================================================
# PATTERN 2: LIST VIEW WITH COLLEGE FILTER
# ============================================================================
@router.get("/example-list", include_in_schema=False)
def list_example(request: Request, db: Session = Depends(get_db)):
    """
    List items for selected college only.
    If no college selected, show empty list.
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    # Get selected college
    college = _get_selected_college(request, db)
    
    # Get items - filter by college if selected
    if not college:
        items = []
    else:
        items = get_college_courses(db, college.id)  # or similar
    
    # Get all colleges for dropdown
    all_colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/template.html", {
        "request": request,
        "title": f"Items - {college.name if college else 'Select College'}",
        "items": items,
        "colleges": all_colleges,
        "selected_college_id": college.id if college else None,
    })


# ============================================================================
# PATTERN 3: CREATE/FORM VIEW
# ============================================================================
@router.get("/example-new", include_in_schema=False)
def new_example_form(request: Request, db: Session = Depends(get_db)):
    """
    Show form to create new item for selected college.
    Only allow if college is selected.
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = _get_selected_college(request, db)
    
    # Require college selection
    if not college:
        return RedirectResponse(url="/admin/example-list?error=select_college")
    
    all_colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/example_form.html", {
        "request": request,
        "title": f"New Item - {college.name}",
        "college": college,
        "colleges": all_colleges,
        "selected_college_id": college.id,
    })


# ============================================================================
# PATTERN 4: CREATE POST - SAVE TO DATABASE
# ============================================================================
@router.post("/example-new", include_in_schema=False)
async def create_example(request: Request, db: Session = Depends(get_db)):
    """
    Create item for selected college.
    Always save to selected college, never ask user for college.
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = _get_selected_college(request, db)
    
    # Safety check - must have college selected
    if not college:
        return RedirectResponse(url="/admin/example-list?error=no_college")
    
    form_data = await request.form()
    
    # Create item - college_id is always from selected college
    item = Course(
        college_id=college.id,  # CRITICAL: Use selected college
        name=form_data.get("name"),
        slug=form_data.get("slug"),
        # ... other fields
    )
    
    db.add(item)
    db.commit()
    
    # Redirect back with college_id preserved in query
    return RedirectResponse(
        url=f"/admin/example-list?college_id={college.id}",
        status_code=303
    )


# ============================================================================
# PATTERN 5: EDIT VIEW - PRE-POPULATE FORM
# ============================================================================
@router.get("/example-{item_id}/edit", include_in_schema=False)
def edit_example_form(request: Request, item_id: int, db: Session = Depends(get_db)):
    """
    Edit form with pre-populated data.
    Verify item belongs to selected college.
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = _get_selected_college(request, db)
    if not college:
        return RedirectResponse(url="/admin/example-list")
    
    # Fetch item
    item = db.query(Course).filter(Course.id == item_id).first()
    
    # Security: Verify item belongs to selected college
    if not item or item.college_id != college.id:
        return RedirectResponse(url="/admin/example-list?error=not_found")
    
    all_colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/example_form.html", {
        "request": request,
        "title": f"Edit: {item.name} - {college.name}",
        "item": item,
        "college": college,
        "colleges": all_colleges,
        "selected_college_id": college.id,
        "is_edit": True,
    })


# ============================================================================
# PATTERN 6: EDIT POST - UPDATE DATABASE
# ============================================================================
@router.post("/example-{item_id}/edit", include_in_schema=False)
async def update_example(request: Request, item_id: int, db: Session = Depends(get_db)):
    """
    Update item in database.
    Verify ownership before updating.
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = _get_selected_college(request, db)
    if not college:
        return RedirectResponse(url="/admin/example-list")
    
    # Fetch item
    item = db.query(Course).filter(Course.id == item_id).first()
    
    # Security: Verify item belongs to selected college
    if not item or item.college_id != college.id:
        return RedirectResponse(url="/admin/example-list?error=not_found")
    
    form_data = await request.form()
    
    # Update fields
    item.name = form_data.get("name", item.name)
    item.slug = form_data.get("slug", item.slug)
    # ... other fields
    
    db.commit()
    
    return RedirectResponse(
        url=f"/admin/example-list?college_id={college.id}",
        status_code=303
    )


# ============================================================================
# PATTERN 7: DELETE - WITH CONFIRMATION
# ============================================================================
@router.post("/example-{item_id}/delete", include_in_schema=False)
def delete_example(request: Request, item_id: int, db: Session = Depends(get_db)):
    """
    Delete item.
    Verify ownership before deleting.
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = _get_selected_college(request, db)
    if not college:
        return RedirectResponse(url="/admin/example-list")
    
    # Fetch item
    item = db.query(Course).filter(Course.id == item_id).first()
    
    # Security: Verify item belongs to selected college
    if not item or item.college_id != college.id:
        return RedirectResponse(url="/admin/example-list?error=not_found")
    
    # Delete
    db.delete(item)
    db.commit()
    
    return RedirectResponse(
        url=f"/admin/example-list?college_id={college.id}",
        status_code=303
    )


# ============================================================================
# PATTERN 8: SPECIAL - CREATE PAGES FOR NEW COLLEGE
# ============================================================================
@router.post("/colleges/new", include_in_schema=False)
async def create_college(request: Request, db: Session = Depends(get_db)):
    """
    When creating new college, auto-generate standard pages.
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    form_data = await request.form()
    
    # Create college
    college = College(
        name=form_data.get("name"),
        slug=form_data.get("slug"),
        is_parent=form_data.get("is_parent") == "on",
        parent_id=form_data.get("parent_id") or None,
    )
    db.add(college)
    db.commit()
    db.refresh(college)
    
    # Auto-create standard pages for this college
    create_standard_pages_for_college(db, college.id, college.name)
    
    return RedirectResponse(url="/admin/colleges", status_code=303)


# ============================================================================
# SUMMARY OF PATTERNS
# ============================================================================
"""
ALWAYS FOLLOW THIS CHECKLIST:

□ GET COLLEGE:
  college = _get_selected_college(request, db)

□ VERIFY COLLEGE SELECTED:
  if not college:
      return RedirectResponse(url="/admin/path")

□ FILTER BY COLLEGE:
  items = db.query(...).filter(Model.college_id == college.id)

□ VERIFY OWNERSHIP (edit/delete):
  if item.college_id != college.id:
      return error

□ SAVE WITH COLLEGE:
  item.college_id = college.id

□ REDIRECT WITH COLLEGE:
  return RedirectResponse(url=f"/admin/path?college_id={college.id}")

□ PASS TO TEMPLATE:
  "selected_college_id": college.id if college else None,
  "colleges": all_colleges,

NEVER:
✗ Hardcode college_id
✗ Show items from all colleges
✗ Trust user input for college_id
✗ Allow editing other college's items
"""
