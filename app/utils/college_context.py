"""
Utilities for managing college context across the admin panel.
Handles college selection, filtering, and hierarchy management.
"""
from sqlalchemy.orm import Session
from app.models.college import College
from app.schemas.schema import Page, Course, Faculty, Placement, Activity, Facility, Admission, Application, Enquiry, MenuItem


def get_college_hierarchy(db: Session, college_id: int = None):
    """
    Get college with children hierarchy.
    If college_id is None, returns all root colleges (is_parent=True or parent_id=None).
    """
    if college_id:
        college = db.query(College).filter(College.id == college_id).first()
        return college
    return db.query(College).filter(College.parent_id == None).all()


def get_child_colleges(db: Session, college_id: int):
    """Get all child colleges for a given parent college."""
    return db.query(College).filter(College.parent_id == college_id).all()


def get_root_college(db: Session, college_id: int):
    """Get the root/parent college in hierarchy."""
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        return None
    if college.parent_id:
        return get_root_college(db, college.parent_id)
    return college


def get_all_colleges_in_hierarchy(db: Session, college_id: int):
    """Get college and all its descendants."""
    result = []
    college = db.query(College).filter(College.id == college_id).first()
    if college:
        result.append(college)
        children = db.query(College).filter(College.parent_id == college_id).all()
        for child in children:
            result.extend(get_all_colleges_in_hierarchy(db, child.id))
    return result


# ========== COLLEGE-SCOPED QUERIES ==========

def get_college_pages(db: Session, college_id: int, include_inherited: bool = False):
    """
    Get pages for a specific college.
    If include_inherited=True, also get pages inherited from parent colleges.
    """
    pages = db.query(Page).filter(Page.college_id == college_id, Page.is_active == True).all()
    
    if include_inherited:
        college = db.query(College).filter(College.id == college_id).first()
        if college and college.parent_id:
            parent_pages = db.query(Page).filter(
                Page.college_id == college.parent_id,
                Page.is_inheritable == True,
                Page.is_active == True
            ).all()
            pages.extend(parent_pages)
    
    return pages


def get_college_courses(db: Session, college_id: int):
    """Get courses for a specific college."""
    return db.query(Course).filter(Course.college_id == college_id, Course.is_active == True).all()


def get_college_faculty(db: Session, college_id: int):
    """Get faculty for a specific college."""
    return db.query(Faculty).filter(Faculty.college_id == college_id, Faculty.is_active == True).all()


def get_college_placements(db: Session, college_id: int):
    """Get placements for a specific college."""
    return db.query(Placement).filter(Placement.college_id == college_id).all()


def get_college_activities(db: Session, college_id: int):
    """Get activities for a specific college."""
    return db.query(Activity).filter(Activity.college_id == college_id).all()


def get_college_facilities(db: Session, college_id: int):
    """Get facilities for a specific college."""
    return db.query(Facility).filter(Facility.college_id == college_id).all()


def get_college_admissions(db: Session, college_id: int):
    """Get admission info for a specific college."""
    return db.query(Admission).filter(Admission.college_id == college_id).first()


def get_college_applications(db: Session, college_id: int):
    """Get applications for a specific college."""
    return db.query(Application).filter(Application.college_id == college_id).all()


def get_college_enquiries(db: Session, college_id: int):
    """Get enquiries for a specific college."""
    return db.query(Enquiry).filter(Enquiry.college_id == college_id).all()


# ========== PAGE MANAGEMENT ==========

def get_or_create_page(db: Session, college_id: int, slug: str, defaults: dict = None):
    """
    Get or create a page for a college.
    Useful for creating standard pages (home, about, etc).
    """
    page = db.query(Page).filter(
        Page.college_id == college_id,
        Page.slug == slug
    ).first()
    
    if not page and defaults:
        page = Page(college_id=college_id, slug=slug, **defaults)
        db.add(page)
        db.commit()
        db.refresh(page)
    
    return page


def inherit_page(db: Session, parent_page_id: int, child_college_id: int):
    """
    Create a page in child college inherited from parent college.
    """
    parent_page = db.query(Page).filter(Page.id == parent_page_id).first()
    if not parent_page or not parent_page.is_inheritable:
        return None
    
    # Check if already inherited
    existing = db.query(Page).filter(
        Page.college_id == child_college_id,
        Page.parent_page_id == parent_page_id
    ).first()
    
    if existing:
        return existing
    
    # Create inherited page
    child_page = Page(
        college_id=child_college_id,
        slug=parent_page.slug,
        title=parent_page.title,
        page_type=parent_page.page_type,
        template_type=parent_page.template_type,
        parent_page_id=parent_page_id,
        is_inheritable=False,
        is_active=parent_page.is_active
    )
    db.add(child_page)
    db.commit()
    db.refresh(child_page)
    
    return child_page


def create_standard_pages_for_college(db: Session, college_id: int, college_name: str):
    """
    Create standard page structure for a new college.
    """
    standard_pages = [
        {"slug": "home", "title": f"{college_name} - Home", "page_type": "HOME", "template_type": "HERO_SECTION"},
        {"slug": "about", "title": f"About {college_name}", "page_type": "ABOUT", "template_type": "BLANK"},
        {"slug": "courses", "title": f"Programs at {college_name}", "page_type": "COURSES", "template_type": "COURSES_LIST"},
        {"slug": "faculty", "title": f"Faculty - {college_name}", "page_type": "FACULTY", "template_type": "FACULTY_LIST"},
        {"slug": "placements", "title": f"Placements - {college_name}", "page_type": "PLACEMENTS", "template_type": "PLACEMENTS"},
        {"slug": "facilities", "title": f"Facilities - {college_name}", "page_type": "FACILITIES", "template_type": "FACILITIES_LIST"},
        {"slug": "admissions", "title": f"Admissions - {college_name}", "page_type": "ADMISSIONS", "template_type": "BLANK"},
        {"slug": "contact", "title": f"Contact {college_name}", "page_type": "CONTACT", "template_type": "BLANK"},
    ]
    
    created_pages = []
    for page_data in standard_pages:
        page = db.query(Page).filter(
            Page.college_id == college_id,
            Page.slug == page_data["slug"]
        ).first()
        
        if not page:
            page = Page(college_id=college_id, is_active=True, **page_data)
            db.add(page)
        
        created_pages.append(page)
    
    db.commit()
    return created_pages
