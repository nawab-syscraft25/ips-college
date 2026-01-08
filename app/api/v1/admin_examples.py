"""
Updated admin.py route examples showing college-scoped queries.
These are examples you should integrate into your existing admin.py
"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.college import College
from app.utils.college_context import (
    get_college_pages,
    get_college_courses,
    get_college_faculty,
    get_college_placements,
    get_college_activities,
    get_college_facilities,
    get_college_admissions,
    get_college_applications,
    get_college_enquiries,
    create_standard_pages_for_college,
)

templates_dir = Path(__file__).resolve().parents[3] / "templet"
templates = Jinja2Templates(directory=str(templates_dir))


def get_selected_college(request: Request, db: Session = Depends(get_db)):
    """
    Helper to get selected college from request state or session.
    Raises 404 if college not found.
    """
    college_id = getattr(request.state, "selected_college_id", None)
    if not college_id:
        college_id = request.session.get("selected_college_id")
    
    if not college_id:
        return None
    
    college = db.query(College).filter(College.id == college_id).first()
    return college


# ==================== PAGES ====================

# @router.get("/pages", include_in_schema=False)
def list_pages_example(request: Request, db: Session = Depends(get_db)):
    """
    Example: List pages for selected college
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = get_selected_college(request, db)
    if not college:
        pages = []
    else:
        pages = get_college_pages(db, college.id)
    
    colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/pages.html", {
        "request": request,
        "title": f"Pages - {college.name if college else 'Select a College'}",
        "pages": pages,
        "colleges": colleges,
        "selected_college_id": college.id if college else None,
    })


# @router.get("/courses", include_in_schema=False)
def list_courses_example(request: Request, db: Session = Depends(get_db)):
    """
    Example: List courses for selected college
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = get_selected_college(request, db)
    if not college:
        courses = []
    else:
        courses = get_college_courses(db, college.id)
    
    colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/courses.html", {
        "request": request,
        "title": f"Courses - {college.name if college else 'Select a College'}",
        "courses": courses,
        "colleges": colleges,
        "selected_college_id": college.id if college else None,
    })


# @router.get("/faculty", include_in_schema=False)
def list_faculty_example(request: Request, db: Session = Depends(get_db)):
    """
    Example: List faculty for selected college
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = get_selected_college(request, db)
    if not college:
        faculty = []
    else:
        faculty = get_college_faculty(db, college.id)
    
    colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/faculty.html", {
        "request": request,
        "title": f"Faculty - {college.name if college else 'Select a College'}",
        "faculty": faculty,
        "colleges": colleges,
        "selected_college_id": college.id if college else None,
    })


# @router.post("/courses/new", include_in_schema=False)
async def create_course_example(request: Request, db: Session = Depends(get_db)):
    """
    Example: Create course for selected college
    """
    college = get_selected_college(request, db)
    if not college:
        return RedirectResponse(url="/admin/courses")
    
    form_data = await request.form()
    
    # Create course
    from app.schemas.schema import Course
    course = Course(
        college_id=college.id,
        name=form_data.get("name"),
        slug=form_data.get("slug"),
        level=form_data.get("level"),
        department=form_data.get("department"),
        duration=form_data.get("duration"),
        fees=form_data.get("fees"),
        eligibility=form_data.get("eligibility"),
        overview=form_data.get("overview"),
    )
    db.add(course)
    db.commit()
    
    return RedirectResponse(url=f"/admin/courses?college_id={college.id}", status_code=303)


# @router.post("/pages/new", include_in_schema=False)
async def create_page_example(request: Request, db: Session = Depends(get_db)):
    """
    Example: Create page for selected college with automatic standard sections
    """
    college = get_selected_college(request, db)
    if not college:
        return RedirectResponse(url="/admin/pages")
    
    form_data = await request.form()
    
    from app.schemas.schema import Page
    page = Page(
        college_id=college.id,
        slug=form_data.get("slug"),
        title=form_data.get("title"),
        page_type=form_data.get("page_type", "STATIC"),
        template_type=form_data.get("template_type"),
        is_inheritable=form_data.get("is_inheritable") == "on",
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    
    # Create SEO metadata
    from app.schemas.schema import SEOMeta
    seo = SEOMeta(
        page_id=page.id,
        meta_title=form_data.get("meta_title"),
        meta_description=form_data.get("meta_description"),
        meta_keywords=form_data.get("meta_keywords"),
        canonical_url=form_data.get("canonical_url"),
        og_title=form_data.get("og_title"),
        og_description=form_data.get("og_description"),
        og_image=form_data.get("og_image"),
    )
    db.add(seo)
    db.commit()
    
    return RedirectResponse(url=f"/admin/pages/{page.id}/sections?college_id={college.id}", status_code=303)


# Example: Show all applications for selected college
# @router.get("/applications", include_in_schema=False)
def list_applications_example(request: Request, db: Session = Depends(get_db)):
    """
    Example: List applications for selected college
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login")
    
    college = get_selected_college(request, db)
    if not college:
        applications = []
    else:
        applications = get_college_applications(db, college.id)
    
    colleges = db.query(College).filter(College.parent_id == None).all()
    
    return templates.TemplateResponse("admin/applications.html", {
        "request": request,
        "title": f"Applications - {college.name if college else 'Select a College'}",
        "applications": applications,
        "colleges": colleges,
        "selected_college_id": college.id if college else None,
    })
