from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.college import College
from app.schemas.schema import (
    Page,
    PageSection,
    SectionItem,
    User,
    Course,
    CoursePage,
    Faculty,
    Placement,
    Activity,
    Facility,
    Admission,
    Application,
    Enquiry,
    MenuItem,
    MediaAsset,
    SEOMeta,
    SharedSection,
    SharedSectionItem,
)
from app.utils.security import verify_password, hash_password

router = APIRouter()

def _require_login(request: Request):
    """
    Simple helper to check admin session.
    """
    user = request.session.get("admin_user")
    if not user:
        return RedirectResponse(url="/admin/login", status_code=303)
    return user


def _ensure_default_admin(db: Session):
    """
    Ensure there is at least one SUPER_ADMIN user in the database.
    Uses ADMIN_PASSWORD from settings for initial bootstrap.
    """
    from app.core.config import settings as _settings

    # Default bootstrap email; can be overridden later from UI or direct DB edit.
    admin_email = getattr(_settings, "ADMIN_EMAIL", None) or "admin@ipsacademy.org"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin_user = User(
            name="Super Admin",
            email=admin_email,
            password=hash_password(_settings.ADMIN_PASSWORD),
            role="SUPER_ADMIN",
            college_id=None,
        )
        db.add(admin_user)
        db.commit()

# Resolve templates directory relative to project root
templates_dir = Path(__file__).resolve().parents[3] / "templet"
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/", include_in_schema=False)
def admin_index(request: Request, db: Session = Depends(get_db)):
    # require login
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    # make sure we always have at least one admin user
    _ensure_default_admin(db)
    colleges = db.query(College).order_by(College.id.desc()).all()
    college_id = request.query_params.get("college_id")
    
    pages = db.query(Page).order_by(Page.id.desc()).all()

    # Dashboard stats
    stats = {
        "colleges": db.query(College).count(),
        "faculty": db.query(Faculty).count(),
        "applications": db.query(Application).count(),
        "enquiries": db.query(Enquiry).count(),
    }

    # Recent applications (most recent 5)
    recent_apps = []
    apps = db.query(Application).order_by(Application.created_at.desc()).limit(5).all()
    for a in apps:
        program = None
        if a.course_id:
            course = db.query(Course).filter(Course.id == a.course_id).first()
            program = course.name if course else "-"
        recent_apps.append(
            {
                "name": a.name,
                "program": program or "-",
                "status": a.status or "",
                "applied_at": a.created_at.strftime("%b %d, %Y") if a.created_at else "",
                "view_url": f"/admin/applications/{a.id}" ,
            }
        )

    return templates.TemplateResponse(
        "admin/index.html",
        {
            "request": request,
            "colleges": colleges,
            "pages": pages,
            "title": "Dashboard",
            "subtitle": "Welcome back to IPS Academy Admin Panel",
            "stats": stats,
            "recent_applications": recent_apps,
            "selected_college_id": college_id or "",
        },
    )


# -------------------
# CMS: Menus
# -------------------
@router.get("/cms/menus", include_in_schema=False)
def list_menus(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(MenuItem).options(joinedload(MenuItem.parent)).order_by(MenuItem.location, MenuItem.parent_id, MenuItem.sort_order)
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(MenuItem.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    menus = q.all()
    pages = db.query(Page).order_by(Page.title).all()
    return templates.TemplateResponse(
        "admin/menus.html",
        {"request": request, "menus": menus, "pages": pages, "colleges": colleges, "selected_college_id": selected_college_id},
    )


@router.get("/cms/menus/new", include_in_schema=False)
def new_menu_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    pages = db.query(Page).order_by(Page.title).all()
    colleges = db.query(College).order_by(College.name).all()
    parents = db.query(MenuItem).order_by(MenuItem.title).all()
    return templates.TemplateResponse(
        "admin/menu_form.html",
        {
            "request": request,
            "action": "create",
            "menu": None,
            "pages": pages,
            "colleges": colleges,
            "parents": parents,
        },
    )


@router.get("/cms/menus/{menu_id}/edit", include_in_schema=False)
def edit_menu_form(request: Request, menu_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    pages = db.query(Page).order_by(Page.title).all()
    colleges = db.query(College).order_by(College.name).all()
    parents = db.query(MenuItem).filter(MenuItem.id != menu_id).order_by(MenuItem.title).all()
    return templates.TemplateResponse(
        "admin/menu_form.html",
        {
            "request": request,
            "action": "edit",
            "menu": menu,
            "pages": pages,
            "colleges": colleges,
            "parents": parents,
        },
    )


@router.post("/cms/menus/new", include_in_schema=False)
async def create_menu(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    menu = MenuItem(
        title=form.get("title"),
        slug=form.get("slug") or None,
        location=form.get("location") or "main",
        url=form.get("url") or None,
        page_id=int(form.get("page_id")) if form.get("page_id") else None,
        college_id=int(form.get("college_id")) if form.get("college_id") else None,
        parent_id=int(form.get("parent_id")) if form.get("parent_id") else None,
        sort_order=int(form.get("sort_order") or 0),
        is_active=bool(form.get("is_active")),
    )
    db.add(menu)
    db.commit()
    return RedirectResponse(url="/admin/cms/menus", status_code=303)


@router.post("/cms/menus/{menu_id}/edit", include_in_schema=False)
async def update_menu(request: Request, menu_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if not menu:
        return RedirectResponse(url="/admin/cms/menus", status_code=303)
    menu.title = form.get("title")
    menu.slug = form.get("slug") or None
    menu.location = form.get("location") or "main"
    menu.url = form.get("url") or None
    menu.page_id = int(form.get("page_id")) if form.get("page_id") else None
    menu.college_id = int(form.get("college_id")) if form.get("college_id") else None
    menu.parent_id = int(form.get("parent_id")) if form.get("parent_id") else None
    menu.sort_order = int(form.get("sort_order") or 0)
    menu.is_active = bool(form.get("is_active"))
    db.add(menu)
    db.commit()
    return RedirectResponse(url="/admin/cms/menus", status_code=303)


@router.post("/cms/menus/{menu_id}/delete", include_in_schema=False)
def delete_menu(request: Request, menu_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    menu = db.query(MenuItem).filter(MenuItem.id == menu_id).first()
    if menu:
        db.delete(menu)
        db.commit()
    return RedirectResponse(url="/admin/cms/menus", status_code=303)


# -------------------
# CMS: Shared Sections (reusable across pages)
# -------------------
@router.get("/cms/shared-sections", include_in_schema=False)
def list_shared_sections(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    sections = db.query(SharedSection).order_by(SharedSection.id.desc()).all()
    return templates.TemplateResponse("admin/shared_sections.html", {"request": request, "sections": sections})


@router.get("/cms/shared-sections/new", include_in_schema=False)
def new_shared_section_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    return templates.TemplateResponse("admin/shared_section_form.html", {"request": request, "action": "create", "section": None})


@router.post("/cms/shared-sections/new", include_in_schema=False)
async def create_shared_section(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    section = SharedSection(
        section_type=form.get("section_type") or "CONTENT",
        section_title=form.get("section_title") or None,
        section_subtitle=form.get("section_subtitle") or None,
        sort_order=int(form.get("sort_order") or 0),
        is_active=bool(form.get("is_active")),
    )
    db.add(section)
    db.commit()
    return RedirectResponse(url="/admin/cms/shared-sections", status_code=303)


@router.get("/cms/shared-sections/{section_id}/edit", include_in_schema=False)
def edit_shared_section_form(request: Request, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    section = db.query(SharedSection).filter(SharedSection.id == section_id).first()
    return templates.TemplateResponse("admin/shared_section_form.html", {"request": request, "action": "edit", "section": section})


@router.post("/cms/shared-sections/{section_id}/edit", include_in_schema=False)
async def update_shared_section(request: Request, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    section = db.query(SharedSection).filter(SharedSection.id == section_id).first()
    if not section:
        return RedirectResponse(url="/admin/cms/shared-sections", status_code=303)
    section.section_type = form.get("section_type") or "CONTENT"
    section.section_title = form.get("section_title") or None
    section.section_subtitle = form.get("section_subtitle") or None
    section.sort_order = int(form.get("sort_order") or 0)
    section.is_active = bool(form.get("is_active"))
    db.add(section)
    db.commit()
    return RedirectResponse(url="/admin/cms/shared-sections", status_code=303)


@router.post("/cms/shared-sections/{section_id}/delete", include_in_schema=False)
def delete_shared_section(request: Request, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    section = db.query(SharedSection).filter(SharedSection.id == section_id).first()
    if section:
        db.delete(section)
        db.commit()
    return RedirectResponse(url="/admin/cms/shared-sections", status_code=303)


# SharedSection items (slides/cards)
@router.get("/cms/shared-sections/{section_id}/items", include_in_schema=False)
def list_shared_section_items(request: Request, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    section = db.query(SharedSection).filter(SharedSection.id == section_id).first()
    if not section:
        return RedirectResponse(url="/admin/cms/shared-sections", status_code=303)
    items = db.query(SharedSectionItem).filter(SharedSectionItem.shared_section_id == section_id).order_by(SharedSectionItem.sort_order).all()
    return templates.TemplateResponse("admin/shared_section_items.html", {"request": request, "section": section, "items": items})


@router.get("/cms/shared-sections/{section_id}/items/new", include_in_schema=False)
def new_shared_section_item_form(request: Request, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    section = db.query(SharedSection).filter(SharedSection.id == section_id).first()
    if not section:
        return RedirectResponse(url="/admin/cms/shared-sections", status_code=303)
    return templates.TemplateResponse("admin/shared_section_item_form.html", {"request": request, "action": "create", "section": section, "item": None})


@router.post("/cms/shared-sections/{section_id}/items/new", include_in_schema=False)
async def create_shared_section_item(request: Request, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    item = SharedSectionItem(
        shared_section_id=section_id,
        title=form.get("title") or None,
        subtitle=form.get("subtitle") or None,
        description=form.get("description") or None,
        image_url=form.get("image_url") or None,
        video_url=form.get("video_url") or None,
        cta_text=form.get("cta_text") or None,
        cta_link=form.get("cta_link") or None,
        extra_data=None,
        sort_order=int(form.get("sort_order") or 0),
    )
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/admin/cms/shared-sections/{section_id}/items", status_code=303)


@router.get("/cms/shared-sections/{section_id}/items/{item_id}/edit", include_in_schema=False)
def edit_shared_section_item_form(request: Request, section_id: int, item_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    section = db.query(SharedSection).filter(SharedSection.id == section_id).first()
    item = db.query(SharedSectionItem).filter(SharedSectionItem.id == item_id, SharedSectionItem.shared_section_id == section_id).first()
    if not section or not item:
        return RedirectResponse(url=f"/admin/cms/shared-sections/{section_id}/items", status_code=303)
    return templates.TemplateResponse("admin/shared_section_item_form.html", {"request": request, "action": "edit", "section": section, "item": item})


@router.post("/cms/shared-sections/{section_id}/items/{item_id}/edit", include_in_schema=False)
async def update_shared_section_item(request: Request, section_id: int, item_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    item = db.query(SharedSectionItem).filter(SharedSectionItem.id == item_id, SharedSectionItem.shared_section_id == section_id).first()
    if not item:
        return RedirectResponse(url=f"/admin/cms/shared-sections/{section_id}/items", status_code=303)
    item.title = form.get("title") or None
    item.subtitle = form.get("subtitle") or None
    item.description = form.get("description") or None
    item.image_url = form.get("image_url") or None
    item.video_url = form.get("video_url") or None
    item.cta_text = form.get("cta_text") or None
    item.cta_link = form.get("cta_link") or None
    item.sort_order = int(form.get("sort_order") or 0)
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/admin/cms/shared-sections/{section_id}/items", status_code=303)


@router.post("/cms/shared-sections/{section_id}/items/{item_id}/delete", include_in_schema=False)
def delete_shared_section_item(request: Request, section_id: int, item_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    item = db.query(SharedSectionItem).filter(SharedSectionItem.id == item_id, SharedSectionItem.shared_section_id == section_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url=f"/admin/cms/shared-sections/{section_id}/items", status_code=303)


# -------------------
# CMS: Media library
# -------------------
@router.get("/cms/media", include_in_schema=False)
def list_media(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    media = db.query(MediaAsset).order_by(MediaAsset.id.desc()).all()
    return templates.TemplateResponse("admin/media.html", {"request": request, "media": media})


@router.get("/cms/media/new", include_in_schema=False)
def new_media_form(request: Request):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    return templates.TemplateResponse(
        "admin/media_form.html",
        {"request": request, "action": "create", "asset": None},
    )


@router.get("/cms/media/{asset_id}/edit", include_in_schema=False)
def edit_media_form(request: Request, asset_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    return templates.TemplateResponse(
        "admin/media_form.html",
        {"request": request, "action": "edit", "asset": asset},
    )


@router.post("/cms/media/new", include_in_schema=False)
async def create_media(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    asset = MediaAsset(
        file_url=form.get("file_url"),
        title=form.get("title") or None,
        alt_text=form.get("alt_text") or None,
        media_type=form.get("media_type") or None,
        meta=None,
    )
    db.add(asset)
    db.commit()
    return RedirectResponse(url="/admin/cms/media", status_code=303)


@router.post("/cms/media/{asset_id}/edit", include_in_schema=False)
async def update_media(request: Request, asset_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    if not asset:
        return RedirectResponse(url="/admin/cms/media", status_code=303)
    asset.file_url = form.get("file_url")
    asset.title = form.get("title") or None
    asset.alt_text = form.get("alt_text") or None
    asset.media_type = form.get("media_type") or None
    db.add(asset)
    db.commit()
    return RedirectResponse(url="/admin/cms/media", status_code=303)


@router.post("/cms/media/{asset_id}/delete", include_in_schema=False)
def delete_media(request: Request, asset_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    if asset:
        db.delete(asset)
        db.commit()
    return RedirectResponse(url="/admin/cms/media", status_code=303)


# -------------------
# Courses (by college)
# -------------------
@router.get("/courses", include_in_schema=False)
def list_courses(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(Course).order_by(Course.id.desc())
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(Course.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    courses = q.all()
    return templates.TemplateResponse(
        "admin/courses.html",
        {"request": request, "courses": courses, "colleges": colleges, "selected_college_id": selected_college_id},
    )


@router.get("/courses/new", include_in_schema=False)
def new_course_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/course_form.html", {"request": request, "action": "create", "course": None, "colleges": colleges})


@router.post("/courses/new", include_in_schema=False)
async def create_course(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    course = Course(
        name=form.get("name"),
        slug=form.get("slug"),
        college_id=int(form.get("college_id")),
        level=form.get("level") or None,
        department=form.get("department") or None,
        duration=form.get("duration") or None,
        fees=form.get("fees") or None,
        eligibility=form.get("eligibility") or None,
        overview=form.get("overview") or None,
        is_active=bool(form.get("is_active")),
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    # Course details
    curriculum_text = form.get("curriculum") or None
    career_text = form.get("career_opportunities") or None
    admission_process = form.get("admission_process") or None
    details = CoursePage(
        course_id=course.id,
        curriculum=curriculum_text if curriculum_text else None,
        career_opportunities=career_text,
        admission_process=admission_process,
    )
    db.add(details)
    db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)


@router.get("/courses/{course_id}/edit", include_in_schema=False)
def edit_course_form(request: Request, course_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    course = db.query(Course).filter(Course.id == course_id).first()
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/course_form.html", {"request": request, "action": "edit", "course": course, "colleges": colleges})


@router.post("/courses/{course_id}/edit", include_in_schema=False)
async def update_course(request: Request, course_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return RedirectResponse(url="/admin/courses", status_code=303)
    course.name = form.get("name")
    course.slug = form.get("slug")
    course.college_id = int(form.get("college_id"))
    course.level = form.get("level") or None
    course.department = form.get("department") or None
    course.duration = form.get("duration") or None
    course.fees = form.get("fees") or None
    course.eligibility = form.get("eligibility") or None
    course.overview = form.get("overview") or None
    course.is_active = bool(form.get("is_active"))

    details = db.query(CoursePage).filter(CoursePage.course_id == course.id).first()
    if not details:
        details = CoursePage(course_id=course.id)
    details.curriculum = (form.get("curriculum") or None)
    details.career_opportunities = form.get("career_opportunities") or None
    details.admission_process = form.get("admission_process") or None

    db.add(course)
    db.add(details)
    db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)


@router.post("/courses/{course_id}/delete", include_in_schema=False)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        db.delete(course)
        db.commit()
    return RedirectResponse(url="/admin/courses", status_code=303)


# ---------
# Faculty
# ---------
@router.get("/faculty", include_in_schema=False)
def list_faculty(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(Faculty).order_by(Faculty.id.desc())
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(Faculty.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    faculty = q.all()
    return templates.TemplateResponse("admin/faculty.html", {"request": request, "faculty": faculty, "colleges": colleges, "selected_college_id": selected_college_id})


@router.get("/faculty/new", include_in_schema=False)
def new_faculty_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/faculty_form.html", {"request": request, "action": "create", "member": None, "colleges": colleges})


@router.post("/faculty/new", include_in_schema=False)
async def create_faculty(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    member = Faculty(
        college_id=int(form.get("college_id")),
        name=form.get("name"),
        designation=form.get("designation") or None,
        qualification=form.get("qualification") or None,
        photo_url=form.get("photo_url") or None,
        bio=form.get("bio") or None,
        is_active=bool(form.get("is_active")),
    )
    db.add(member)
    db.commit()
    return RedirectResponse(url="/admin/faculty", status_code=303)


@router.get("/faculty/{member_id}/edit", include_in_schema=False)
def edit_faculty_form(request: Request, member_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    member = db.query(Faculty).filter(Faculty.id == member_id).first()
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/faculty_form.html", {"request": request, "action": "edit", "member": member, "colleges": colleges})


@router.post("/faculty/{member_id}/edit", include_in_schema=False)
async def update_faculty(request: Request, member_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    member = db.query(Faculty).filter(Faculty.id == member_id).first()
    if not member:
        return RedirectResponse(url="/admin/faculty", status_code=303)
    member.college_id = int(form.get("college_id"))
    member.name = form.get("name")
    member.designation = form.get("designation") or None
    member.qualification = form.get("qualification") or None
    member.photo_url = form.get("photo_url") or None
    member.bio = form.get("bio") or None
    member.is_active = bool(form.get("is_active"))
    db.add(member)
    db.commit()
    return RedirectResponse(url="/admin/faculty", status_code=303)


@router.post("/faculty/{member_id}/delete", include_in_schema=False)
def delete_faculty(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Faculty).filter(Faculty.id == member_id).first()
    if member:
        db.delete(member)
        db.commit()
    return RedirectResponse(url="/admin/faculty", status_code=303)


# -----------
# Placements
# -----------
@router.get("/placements", include_in_schema=False)
def list_placements(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(Placement).order_by(Placement.id.desc())
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(Placement.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    placements = q.all()
    return templates.TemplateResponse("admin/placements.html", {"request": request, "placements": placements, "colleges": colleges, "selected_college_id": selected_college_id})


@router.get("/placements/new", include_in_schema=False)
def new_placement_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/placement_form.html", {"request": request, "action": "create", "placement": None, "colleges": colleges})


@router.post("/placements/new", include_in_schema=False)
async def create_placement(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    placement = Placement(
        college_id=int(form.get("college_id")),
        year=int(form.get("year")),
        highest_package=float(form.get("highest_package") or 0),
        average_package=float(form.get("average_package") or 0),
        placement_percentage=float(form.get("placement_percentage") or 0),
    )
    db.add(placement)
    db.commit()
    return RedirectResponse(url="/admin/placements", status_code=303)


@router.get("/placements/{placement_id}/edit", include_in_schema=False)
def edit_placement_form(request: Request, placement_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    placement = db.query(Placement).filter(Placement.id == placement_id).first()
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/placement_form.html", {"request": request, "action": "edit", "placement": placement, "colleges": colleges})


@router.post("/placements/{placement_id}/edit", include_in_schema=False)
async def update_placement(request: Request, placement_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    placement = db.query(Placement).filter(Placement.id == placement_id).first()
    if not placement:
        return RedirectResponse(url="/admin/placements", status_code=303)
    placement.college_id = int(form.get("college_id"))
    placement.year = int(form.get("year"))
    placement.highest_package = float(form.get("highest_package") or 0)
    placement.average_package = float(form.get("average_package") or 0)
    placement.placement_percentage = float(form.get("placement_percentage") or 0)
    db.add(placement)
    db.commit()
    return RedirectResponse(url="/admin/placements", status_code=303)


@router.post("/placements/{placement_id}/delete", include_in_schema=False)
def delete_placement(placement_id: int, db: Session = Depends(get_db)):
    placement = db.query(Placement).filter(Placement.id == placement_id).first()
    if placement:
        db.delete(placement)
        db.commit()
    return RedirectResponse(url="/admin/placements", status_code=303)


# ----------
# Activities
# ----------
@router.get("/activities", include_in_schema=False)
def list_activities(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(Activity).order_by(Activity.id.desc())
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(Activity.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    activities = q.all()
    return templates.TemplateResponse("admin/activities.html", {"request": request, "activities": activities, "colleges": colleges, "selected_college_id": selected_college_id})


@router.get("/activities/new", include_in_schema=False)
def new_activity_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/activity_form.html", {"request": request, "action": "create", "activity": None, "colleges": colleges})


@router.post("/activities/new", include_in_schema=False)
async def create_activity(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    activity = Activity(
        college_id=int(form.get("college_id")),
        type=form.get("type") or None,
        title=form.get("title"),
        description=form.get("description") or None,
        image_url=form.get("image_url") or None,
        event_date=form.get("event_date") or None,
    )
    db.add(activity)
    db.commit()
    return RedirectResponse(url="/admin/activities", status_code=303)


@router.get("/activities/{activity_id}/edit", include_in_schema=False)
def edit_activity_form(request: Request, activity_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/activity_form.html", {"request": request, "action": "edit", "activity": activity, "colleges": colleges})


@router.post("/activities/{activity_id}/edit", include_in_schema=False)
async def update_activity(request: Request, activity_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        return RedirectResponse(url="/admin/activities", status_code=303)
    activity.college_id = int(form.get("college_id"))
    activity.type = form.get("type") or None
    activity.title = form.get("title")
    activity.description = form.get("description") or None
    activity.image_url = form.get("image_url") or None
    activity.event_date = form.get("event_date") or None
    db.add(activity)
    db.commit()
    return RedirectResponse(url="/admin/activities", status_code=303)


@router.post("/activities/{activity_id}/delete", include_in_schema=False)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if activity:
        db.delete(activity)
        db.commit()
    return RedirectResponse(url="/admin/activities", status_code=303)


# ----------
# Facilities
# ----------
@router.get("/facilities", include_in_schema=False)
def list_facilities(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(Facility).order_by(Facility.id.desc())
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(Facility.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    facilities = q.all()
    return templates.TemplateResponse("admin/facilities.html", {"request": request, "facilities": facilities, "colleges": colleges, "selected_college_id": selected_college_id})


@router.get("/facilities/new", include_in_schema=False)
def new_facility_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/facility_form.html", {"request": request, "action": "create", "facility": None, "colleges": colleges})


@router.post("/facilities/new", include_in_schema=False)
async def create_facility(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    facility = Facility(
        college_id=int(form.get("college_id")),
        name=form.get("name"),
        description=form.get("description") or None,
        image_url=form.get("image_url") or None,
    )
    db.add(facility)
    db.commit()
    return RedirectResponse(url="/admin/facilities", status_code=303)


@router.get("/facilities/{facility_id}/edit", include_in_schema=False)
def edit_facility_form(request: Request, facility_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/facility_form.html", {"request": request, "action": "edit", "facility": facility, "colleges": colleges})


@router.post("/facilities/{facility_id}/edit", include_in_schema=False)
async def update_facility(request: Request, facility_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        return RedirectResponse(url="/admin/facilities", status_code=303)
    facility.college_id = int(form.get("college_id"))
    facility.name = form.get("name")
    facility.description = form.get("description") or None
    facility.image_url = form.get("image_url") or None
    db.add(facility)
    db.commit()
    return RedirectResponse(url="/admin/facilities", status_code=303)


@router.post("/facilities/{facility_id}/delete", include_in_schema=False)
def delete_facility(facility_id: int, db: Session = Depends(get_db)):
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if facility:
        db.delete(facility)
        db.commit()
    return RedirectResponse(url="/admin/facilities", status_code=303)


# -----------
# Admissions
# -----------
@router.get("/admissions", include_in_schema=False)
def list_admissions(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(Admission).order_by(Admission.id.desc())
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(Admission.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    admissions = q.all()
    return templates.TemplateResponse("admin/admissions.html", {"request": request, "admissions": admissions, "colleges": colleges, "selected_college_id": selected_college_id})


@router.get("/admissions/new", include_in_schema=False)
def new_admission_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/admission_form.html", {"request": request, "action": "create", "admission": None, "colleges": colleges})


@router.post("/admissions/new", include_in_schema=False)
async def create_admission(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    admission = Admission(
        college_id=int(form.get("college_id")),
        procedure_text=form.get("procedure_text") or None,
        eligibility_text=form.get("eligibility_text") or None,
    )
    db.add(admission)
    db.commit()
    return RedirectResponse(url="/admin/admissions", status_code=303)


@router.get("/admissions/{admission_id}/edit", include_in_schema=False)
def edit_admission_form(request: Request, admission_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    admission = db.query(Admission).filter(Admission.id == admission_id).first()
    colleges = db.query(College).all()
    return templates.TemplateResponse("admin/admission_form.html", {"request": request, "action": "edit", "admission": admission, "colleges": colleges})


@router.post("/admissions/{admission_id}/edit", include_in_schema=False)
async def update_admission(request: Request, admission_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    admission = db.query(Admission).filter(Admission.id == admission_id).first()
    if not admission:
        return RedirectResponse(url="/admin/admissions", status_code=303)
    admission.college_id = int(form.get("college_id"))
    admission.procedure_text = form.get("procedure_text") or None
    admission.eligibility_text = form.get("eligibility_text") or None
    db.add(admission)
    db.commit()
    return RedirectResponse(url="/admin/admissions", status_code=303)


@router.post("/admissions/{admission_id}/delete", include_in_schema=False)
def delete_admission(admission_id: int, db: Session = Depends(get_db)):
    admission = db.query(Admission).filter(Admission.id == admission_id).first()
    if admission:
        db.delete(admission)
        db.commit()
    return RedirectResponse(url="/admin/admissions", status_code=303)


# --------------
# Applications (read/update status)
# --------------
@router.get("/applications", include_in_schema=False)
def list_applications(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(Application).order_by(Application.id.desc())
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(Application.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    applications = q.all()
    return templates.TemplateResponse("admin/applications.html", {"request": request, "applications": applications, "colleges": colleges, "selected_college_id": selected_college_id})


@router.post("/applications/{app_id}/status", include_in_schema=False)
async def update_application_status(request: Request, app_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    status = form.get("status") or None
    app = db.query(Application).filter(Application.id == app_id).first()
    if app:
        app.status = status
        db.add(app)
        db.commit()
    return RedirectResponse(url="/admin/applications", status_code=303)


# --------------
# Enquiries (read)
# --------------
@router.get("/enquiries", include_in_schema=False)
def list_enquiries(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.name).all()
    college_id = request.query_params.get("college_id")
    q = db.query(Enquiry).order_by(Enquiry.id.desc())
    selected_college_id = None
    if college_id:
        try:
            selected_college_id = int(college_id)
            q = q.filter(Enquiry.college_id == selected_college_id)
        except Exception:
            selected_college_id = None
    enquiries = q.all()
    return templates.TemplateResponse("admin/enquiries.html", {"request": request, "enquiries": enquiries, "colleges": colleges, "selected_college_id": selected_college_id})

@router.get("/colleges", include_in_schema=False)
def list_colleges(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    colleges = db.query(College).order_by(College.id.desc()).all()
    return templates.TemplateResponse("admin/colleges.html", {"request": request, "colleges": colleges})

@router.get("/colleges/new", include_in_schema=False)
def new_college_form(request: Request):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    # pass list of existing colleges so admin can choose a parent
    # import db lazily to avoid changing signature
    from app.core.database import SessionLocal
    db = SessionLocal()
    colleges = db.query(College).order_by(College.name).all()
    db.close()
    return templates.TemplateResponse("admin/college_form.html", {"request": request, "action": "create", "college": None, "colleges": colleges})

@router.post("/colleges/new", include_in_schema=False)
async def create_college(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    name = form.get("name")
    slug = form.get("slug")
    subdomain = form.get("subdomain")
    short_description = form.get("short_description")
    theme_primary_color = form.get("theme_primary_color")
    theme_secondary_color = form.get("theme_secondary_color")
    is_active = bool(form.get("is_active"))

    parent_id = form.get("parent_id") or None
    if parent_id == "":
        parent_id = None
    else:
        try:
            parent_id = int(parent_id)
        except Exception:
            parent_id = None

    college = College(
        name=name,
        slug=slug,
        subdomain=subdomain or None,
        short_description=short_description,
        theme_primary_color=theme_primary_color,
        theme_secondary_color=theme_secondary_color,
        is_active=is_active,
        parent_id=parent_id,
    )
    db.add(college)
    db.commit()
    db.refresh(college)
    return RedirectResponse(url="/admin/colleges", status_code=303)

@router.get("/colleges/{college_id}/edit", include_in_schema=False)
def edit_college_form(request: Request, college_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    college = db.query(College).filter(College.id == college_id).first()
    # provide list of possible parents (exclude self)
    colleges = db.query(College).filter(College.id != college_id).order_by(College.name).all()
    return templates.TemplateResponse("admin/college_form.html", {"request": request, "action": "edit", "college": college, "colleges": colleges})

@router.post("/colleges/{college_id}/edit", include_in_schema=False)
async def update_college(request: Request, college_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        return RedirectResponse(url="/admin/colleges", status_code=303)
    college.name = form.get("name")
    college.slug = form.get("slug")
    college.subdomain = form.get("subdomain") or None
    college.short_description = form.get("short_description")
    college.theme_primary_color = form.get("theme_primary_color")
    college.theme_secondary_color = form.get("theme_secondary_color")
    college.is_active = bool(form.get("is_active"))
    parent_id = form.get("parent_id") or None
    if parent_id == "":
        parent_id = None
    else:
        try:
            parent_id = int(parent_id)
        except Exception:
            parent_id = None
    # Prevent setting the college as its own parent
    if parent_id == college.id:
        parent_id = None
    college.parent_id = parent_id
    db.add(college)
    db.commit()
    return RedirectResponse(url="/admin/colleges", status_code=303)

@router.post("/colleges/{college_id}/delete", include_in_schema=False)
def delete_college(college_id: int, db: Session = Depends(get_db)):
    # require login
    # note: use RedirectResponse check
    # incoming request not available here; use dependency-less delete route for now
    college = db.query(College).filter(College.id == college_id).first()
    if college:
        db.delete(college)
        db.commit()
    return RedirectResponse(url="/admin/colleges", status_code=303)

# Pages: list, new, edit, delete
@router.get("/pages", include_in_schema=False)
def list_pages(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    
    # Get college context
    college_id = request.query_params.get("college_id")
    selected_college = None
    if college_id:
        selected_college = db.query(College).filter(College.id == int(college_id)).first()
    
    # Filter pages by college if specified
    if college_id:
        pages = db.query(Page).filter(Page.college_id == int(college_id)).order_by(Page.id.desc()).all()
    else:
        pages = db.query(Page).order_by(Page.id.desc()).all()
    
    colleges = db.query(College).order_by(College.name).all()
    
    return templates.TemplateResponse(
        "admin/pages_list.html", 
        {
            "request": request, 
            "pages": pages,
            "colleges": colleges,
            "selected_college": selected_college,
            "selected_college_id": college_id or ""
        }
    )


# -------------------
# CMS: Page sections (builder)
# -------------------
@router.get("/pages/{page_id}/sections", include_in_schema=False)
def list_page_sections(request: Request, page_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    page = db.query(Page).filter(Page.id == page_id).first()
    sections = db.query(PageSection).filter(PageSection.page_id == page_id).order_by(PageSection.sort_order).all()
    return templates.TemplateResponse(
        "admin/page_sections.html",
        {"request": request, "page": page, "sections": sections},
    )


@router.get("/pages/{page_id}/sections/new", include_in_schema=False)
def new_page_section_form(request: Request, page_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    page = db.query(Page).filter(Page.id == page_id).first()
    return templates.TemplateResponse(
        "admin/section_form.html",
        {"request": request, "action": "create", "page": page, "section": None},
    )


@router.post("/pages/{page_id}/sections/new", include_in_schema=False)
async def create_page_section(request: Request, page_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    
    section_type = form.get("section_type") or "CONTENT"
    extra_data = {}
    
    # Handle type-specific data (HERO section)
    if section_type == "HERO":
        extra_data['hero_style'] = form.get("hero_style") or "overlay"
        extra_data['hero_text_color'] = form.get("hero_text_color") or "white"
        extra_data['hero_height'] = form.get("hero_height") or "medium"
        extra_data['hero_cta_text'] = form.get("hero_cta_text") or None
        extra_data['hero_cta_link'] = form.get("hero_cta_link") or None
    
    section = PageSection(
        page_id=page_id,
        section_type=section_type,
        section_title=form.get("section_title") or None,
        section_subtitle=form.get("section_subtitle") or None,
        sort_order=int(form.get("sort_order") or 0),
        is_active=bool(form.get("is_active")),
        extra_data=extra_data if extra_data else None
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    
    # Handle hero image upload after section is created (we need the section ID)
    if section_type == "HERO":
        hero_image = form.get("hero_image")
        if hero_image and hasattr(hero_image, 'filename') and hero_image.filename:
            import os
            from pathlib import Path
            upload_dir = Path("templet/static/uploads/hero")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"hero_{section.id}_{hero_image.filename}"
            filepath = upload_dir / filename
            content = await hero_image.read()
            with open(filepath, 'wb') as f:
                f.write(content)
            
            section.extra_data['hero_image_url'] = f"/static/uploads/hero/{filename}"
            db.add(section)
            db.commit()
    
    return RedirectResponse(url=f"/admin/pages/{page_id}/sections", status_code=303)


@router.get("/pages/{page_id}/sections/{section_id}/edit", include_in_schema=False)
def edit_page_section_form(request: Request, page_id: int, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    page = db.query(Page).filter(Page.id == page_id).first()
    section = db.query(PageSection).filter(PageSection.id == section_id).first()
    return templates.TemplateResponse(
        "admin/section_form.html",
        {"request": request, "action": "edit", "page": page, "section": section},
    )


@router.post("/pages/{page_id}/sections/{section_id}/edit", include_in_schema=False)
async def update_page_section(request: Request, page_id: int, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    section = db.query(PageSection).filter(PageSection.id == section_id).first()
    if not section:
        return RedirectResponse(url=f"/admin/pages/{page_id}/sections", status_code=303)
    
    section.section_type = form.get("section_type") or "CONTENT"
    section.section_title = form.get("section_title") or None
    section.section_subtitle = form.get("section_subtitle") or None
    section.sort_order = int(form.get("sort_order") or 0)
    section.is_active = bool(form.get("is_active"))
    
    # Handle type-specific data (HERO section)
    extra_data = section.extra_data or {}
    if section.section_type == "HERO":
        # Handle hero image upload
        hero_image = form.get("hero_image")
        if hero_image and hasattr(hero_image, 'filename') and hero_image.filename:
            import os
            from pathlib import Path
            upload_dir = Path("templet/static/uploads/hero")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"hero_{section_id}_{hero_image.filename}"
            filepath = upload_dir / filename
            content = await hero_image.read()
            with open(filepath, 'wb') as f:
                f.write(content)
            extra_data['hero_image_url'] = f"/static/uploads/hero/{filename}"
        
        # Keep existing image if no new one uploaded
        if not hero_image or not hasattr(hero_image, 'filename') or not hero_image.filename:
            if form.get("existing_hero_image"):
                extra_data['hero_image_url'] = form.get("existing_hero_image")
        
        # Save other hero settings
        extra_data['hero_cta_text'] = form.get("hero_cta_text") or None
        extra_data['hero_cta_link'] = form.get("hero_cta_link") or None
        extra_data['hero_style'] = form.get("hero_style") or "overlay"
        extra_data['hero_text_color'] = form.get("hero_text_color") or "white"
        extra_data['hero_height'] = form.get("hero_height") or "medium"
    
    section.extra_data = extra_data
    db.add(section)
    db.commit()
    return RedirectResponse(url=f"/admin/pages/{page_id}/sections", status_code=303)


@router.post("/pages/{page_id}/sections/{section_id}/delete", include_in_schema=False)
def delete_page_section(request: Request, page_id: int, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    section = db.query(PageSection).filter(PageSection.id == section_id).first()
    if section:
        db.delete(section)
        db.commit()
    return RedirectResponse(url=f"/admin/pages/{page_id}/sections", status_code=303)


@router.get("/pages/{page_id}/sections/{section_id}/items/new", include_in_schema=False)
def new_section_item_form(request: Request, page_id: int, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    section = db.query(PageSection).filter(PageSection.id == section_id).first()
    return templates.TemplateResponse(
        "admin/section_item_form.html",
        {"request": request, "action": "create", "section": section, "item": None, "page_id": page_id},
    )


@router.get("/pages/{page_id}/sections/{section_id}/items/{item_id}/edit", include_in_schema=False)
def edit_section_item_form(request: Request, page_id: int, section_id: int, item_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    section = db.query(PageSection).filter(PageSection.id == section_id).first()
    item = db.query(SectionItem).filter(SectionItem.id == item_id).first()
    return templates.TemplateResponse(
        "admin/section_item_form.html",
        {"request": request, "action": "edit", "section": section, "item": item, "page_id": page_id},
    )


@router.post("/pages/{page_id}/sections/{section_id}/items/new", include_in_schema=False)
async def create_section_item(request: Request, page_id: int, section_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    item = SectionItem(
        section_id=section_id,
        title=form.get("title") or None,
        subtitle=form.get("subtitle") or None,
        description=form.get("description") or None,
        image_url=form.get("image_url") or None,
        video_url=form.get("video_url") or None,
        cta_text=form.get("cta_text") or None,
        cta_link=form.get("cta_link") or None,
        extra_data=None,
        sort_order=int(form.get("sort_order") or 0),
    )
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/admin/pages/{page_id}/sections", status_code=303)


@router.post("/pages/{page_id}/sections/{section_id}/items/{item_id}/edit", include_in_schema=False)
async def update_section_item(request: Request, page_id: int, section_id: int, item_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    item = db.query(SectionItem).filter(SectionItem.id == item_id).first()
    if not item:
        return RedirectResponse(url=f"/admin/pages/{page_id}/sections", status_code=303)
    item.title = form.get("title") or None
    item.subtitle = form.get("subtitle") or None
    item.description = form.get("description") or None
    item.image_url = form.get("image_url") or None
    item.video_url = form.get("video_url") or None
    item.cta_text = form.get("cta_text") or None
    item.cta_link = form.get("cta_link") or None
    item.sort_order = int(form.get("sort_order") or 0)
    db.add(item)
    db.commit()
    return RedirectResponse(url=f"/admin/pages/{page_id}/sections", status_code=303)


@router.post("/pages/{page_id}/sections/{section_id}/items/{item_id}/delete", include_in_schema=False)
def delete_section_item(request: Request, page_id: int, section_id: int, item_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    item = db.query(SectionItem).filter(SectionItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url=f"/admin/pages/{page_id}/sections", status_code=303)

@router.get("/pages/new", include_in_schema=False)
@router.get("/page/new", include_in_schema=False)
def new_page_form(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    
    college_id = request.query_params.get("college_id")
    colleges = db.query(College).order_by(College.name).all()
    shared_sections = db.query(SharedSection).order_by(SharedSection.sort_order).all()
    
    return templates.TemplateResponse(
        "admin/page_form.html",
        {
            "request": request, 
            "action": "create", 
            "page": None, 
            "colleges": colleges, 
            "shared_sections": shared_sections,
            "selected_college_id": college_id or ""
        },
    )

@router.post("/pages/new", include_in_schema=False)
@router.post("/page/new", include_in_schema=False)
async def create_page(request: Request, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    college_id = request.query_params.get("college_id")
    
    title = form.get("title")
    slug_input = form.get("slug")
    college_id_form = form.get("college_id") or None
    is_active_value = form.get("is_active", "1")
    is_active = is_active_value in ('1', 'on', 'true', True)
    is_inheritable = bool(form.get("is_inheritable"))
    
    # Generate slug from title if not provided
    if slug_input:
        slug = slug_input
    else:
        # Auto-generate slug from title
        import re
        slug = title.lower().strip() if title else "page"
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = slug.strip('-')
    
    page = Page(
        title=title, 
        slug=slug, 
        college_id=int(college_id_form) if college_id_form else None,
        is_active=is_active,
        is_inheritable=is_inheritable
    )
    db.add(page)
    db.commit()
    db.refresh(page)

    # attach shared sections if any selected
    try:
        selected = form.getlist("shared_section_ids")
    except Exception:
        selected = form.get("shared_section_ids")
    if selected:
        if isinstance(selected, str):
            selected = [selected]
        try:
            ids = [int(x) for x in selected if x]
            if ids:
                sections = db.query(SharedSection).filter(SharedSection.id.in_(ids)).all()
                page.shared_sections = sections
                db.add(page)
                db.commit()
        except Exception:
            pass

    # handle SEO meta if provided
    meta_title = form.get("meta_title") or None
    meta_description = form.get("meta_description") or None
    meta_keywords = form.get("meta_keywords") or None
    canonical_url = form.get("canonical_url") or None
    og_title = form.get("og_title") or None
    og_description = form.get("og_description") or None
    og_image = form.get("og_image") or None
    schema_json = form.get("schema_json") or None
    if any([meta_title, meta_description, meta_keywords, canonical_url, og_title, og_description, og_image, schema_json]):
        seo = SEOMeta(
            page_id=page.id,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            canonical_url=canonical_url,
            og_title=og_title,
            og_description=og_description,
            og_image=og_image,
            schema_json=schema_json,
        )
        db.add(seo)
        db.commit()
    
    redirect_url = f"/admin/pages?college_id={college_id}" if college_id else "/admin/pages"
    return RedirectResponse(url=redirect_url, status_code=303)

@router.get("/pages/{page_id}/edit", include_in_schema=False)
def edit_page_form(request: Request, page_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    
    college_id = request.query_params.get("college_id")
    page = db.query(Page).filter(Page.id == page_id).first()
    colleges = db.query(College).order_by(College.name).all()
    shared_sections = db.query(SharedSection).order_by(SharedSection.sort_order).all()
    
    return templates.TemplateResponse(
        "admin/page_form.html",
        {
            "request": request, 
            "action": "edit", 
            "page": page, 
            "colleges": colleges, 
            "shared_sections": shared_sections,
            "selected_college_id": college_id or ""
        },
    )

@router.post("/pages/{page_id}/edit", include_in_schema=False)
async def update_page(request: Request, page_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    form = await request.form()
    college_id = request.query_params.get("college_id")
    
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page:
        redirect_url = f"/admin/pages?college_id={college_id}" if college_id else "/admin/pages"
        return RedirectResponse(url=redirect_url, status_code=303)
    
    page.title = form.get("title")
    
    # Generate slug from title if not provided
    slug_input = form.get("slug")
    if slug_input:
        page.slug = slug_input
    else:
        # Auto-generate slug from title
        import re
        slug = page.title.lower().strip() if page.title else "page"
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = slug.strip('-')
        page.slug = slug
    
    college_id_form = form.get("college_id") or None
    page.college_id = int(college_id_form) if college_id_form else None
    # Handle is_active properly - check if value is '1' or 'on'
    is_active_value = form.get("is_active", "0")
    page.is_active = is_active_value in ('1', 'on', 'true', True)
    page.is_inheritable = bool(form.get("is_inheritable"))

    # update or create SEO meta
    meta_title = form.get("meta_title") or None
    meta_description = form.get("meta_description") or None
    meta_keywords = form.get("meta_keywords") or None
    canonical_url = form.get("canonical_url") or None
    og_title = form.get("og_title") or None
    og_description = form.get("og_description") or None
    og_image = form.get("og_image") or None
    schema_json = form.get("schema_json") or None

    seo = db.query(SEOMeta).filter(SEOMeta.page_id == page.id).first()
    if seo:
        seo.meta_title = meta_title
        seo.meta_description = meta_description
        seo.meta_keywords = meta_keywords
        seo.canonical_url = canonical_url
        seo.og_title = og_title
        seo.og_description = og_description
        seo.og_image = og_image
        seo.schema_json = schema_json
        db.add(seo)
    else:
        if any([meta_title, meta_description, meta_keywords, canonical_url, og_title, og_description, og_image, schema_json]):
            seo = SEOMeta(
                page_id=page.id,
                meta_title=meta_title,
                meta_description=meta_description,
                meta_keywords=meta_keywords,
                canonical_url=canonical_url,
                og_title=og_title,
                og_description=og_description,
                og_image=og_image,
                schema_json=schema_json,
            )
            db.add(seo)

    db.add(page)
    db.commit()
    # handle shared sections selection
    try:
        selected = form.getlist("shared_section_ids")
    except Exception:
        selected = form.get("shared_section_ids")
    if selected is None:
        # if nothing selected, clear associations
        page.shared_sections = []
        db.add(page)
        db.commit()
    else:
        if isinstance(selected, str):
            selected = [selected]
        try:
            ids = [int(x) for x in selected if x]
            sections = db.query(SharedSection).filter(SharedSection.id.in_(ids)).all() if ids else []
            page.shared_sections = sections
            db.add(page)
            db.commit()
        except Exception:
            pass
    
    redirect_url = f"/admin/pages?college_id={college_id}" if college_id else "/admin/pages"
    return RedirectResponse(url=redirect_url, status_code=303)

@router.post("/pages/{page_id}/delete", include_in_schema=False)
def delete_page(request: Request, page_id: int, db: Session = Depends(get_db)):
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    page = db.query(Page).filter(Page.id == page_id).first()
    college_id = request.query_params.get("college_id")
    if page:
        db.delete(page)
        db.commit()
    redirect_url = f"/admin/pages?college_id={college_id}" if college_id else "/admin/pages"
    return RedirectResponse(url=redirect_url, status_code=303)


# ===== NEW MODERN UI ROUTES =====

@router.get("/page/{page_id}/design", include_in_schema=False)
def page_designer(request: Request, page_id: int, db: Session = Depends(get_db)):
    """WordPress-like page designer with drag-drop sections"""
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    
    college_id = request.query_params.get("college_id")
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page:
        return RedirectResponse(url="/admin/pages", status_code=303)
    
    # Use page's college_id if not provided in query params
    if not college_id and page.college_id:
        college_id = str(page.college_id)
    
    sections = db.query(PageSection).filter(PageSection.page_id == page_id).order_by(PageSection.sort_order).all()
    
    return templates.TemplateResponse(
        "admin/page_builder.html",
        {
            "request": request,
            "page": page,
            "sections": sections,
            "selected_college_id": college_id or ""
        }
    )


@router.get("/page/{page_id}/seo", include_in_schema=False)
def page_seo_editor(request: Request, page_id: int, db: Session = Depends(get_db)):
    """Professional SEO optimization panel"""
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    
    college_id = request.query_params.get("college_id")
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page:
        return RedirectResponse(url="/admin/pages", status_code=303)
    
    seo = db.query(SEOMeta).filter(SEOMeta.page_id == page_id).first()
    
    return templates.TemplateResponse(
        "admin/page_seo.html",
        {
            "request": request,
            "page": page,
            "seo": seo,
            "selected_college_id": college_id or ""
        }
    )


@router.post("/page/{page_id}/seo", include_in_schema=False)
async def update_page_seo(request: Request, page_id: int, db: Session = Depends(get_db)):
    """Save SEO settings"""
    if isinstance(_require_login(request), RedirectResponse):
        return _require_login(request)
    
    form = await request.form()
    college_id = request.query_params.get("college_id")
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page:
        return RedirectResponse(url="/admin/pages", status_code=303)
    
    # Update SEO meta
    seo = db.query(SEOMeta).filter(SEOMeta.page_id == page_id).first()
    if seo:
        seo.meta_title = form.get("meta_title") or None
        seo.meta_description = form.get("meta_description") or None
        seo.meta_keywords = form.get("meta_keywords") or None
        seo.og_title = form.get("og_title") or None
        seo.og_description = form.get("og_description") or None
        seo.og_image = form.get("og_image") or None
        seo.canonical_url = form.get("canonical_url") or None
        seo.schema_json = form.get("schema_json") or None
        db.add(seo)
    else:
        seo = SEOMeta(
            page_id=page_id,
            meta_title=form.get("meta_title") or None,
            meta_description=form.get("meta_description") or None,
            meta_keywords=form.get("meta_keywords") or None,
            og_title=form.get("og_title") or None,
            og_description=form.get("og_description") or None,
            og_image=form.get("og_image") or None,
            canonical_url=form.get("canonical_url") or None,
            schema_json=form.get("schema_json") or None,
        )
        db.add(seo)
    
    db.commit()
    redirect_url = f"/admin/page/{page_id}/seo?college_id={college_id}" if college_id else f"/admin/page/{page_id}/seo"
    return RedirectResponse(url=redirect_url, status_code=303)


# --- Login / logout routes ---
@router.get("/login", include_in_schema=False)
def login_form(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login", include_in_schema=False)
async def login_post(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username") or ""
    password = form.get("password") or ""

    # Make sure default SUPER_ADMIN exists before authenticating
    _ensure_default_admin(db)

    # Try to authenticate against stored users
    user = db.query(User).filter(User.email == username).first()

    if user and verify_password(password, user.password):
        request.session["admin_user"] = {
            "id": user.id,
            "username": user.name,
            "role": user.role,
        }
        return RedirectResponse(url="/admin", status_code=303)

    # failed
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": "Invalid username or password"},
    )


@router.get("/logout", include_in_schema=False)
def logout(request: Request):
    request.session.pop("admin_user", None)
    return RedirectResponse(url="/admin/login", status_code=303)
