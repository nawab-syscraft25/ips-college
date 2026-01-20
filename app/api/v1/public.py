"""
Public API routes for frontend website consumption.
These routes are publicly accessible without authentication.
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.college import College
from app.schemas.schema import (
    Page,
    Course,
    Faculty,
    Placement,
    Activity,
    Facility,
    Admission,
    Application,
    Enquiry,
    SEOMeta,
    PageSection,
    SectionItem,
    CoursePage,
)
from datetime import datetime
from typing import Optional, List


# =====================================
# Request Models
# =====================================

class ApplicationSubmitRequest(BaseModel):
    college_id: int
    name: str
    email: str
    phone: str
    course_id: Optional[int] = None
    documents: Optional[dict] = None


class EnquirySubmitRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None
    college_id: Optional[int] = None

router = APIRouter()

# =====================================
# COLLEGES - Public Routes
# =====================================

@router.get("/colleges")
def list_colleges(db: Session = Depends(get_db)):
    """
    Get all active colleges for navigation/directory.
    """
    colleges = db.query(College).filter(College.is_active == True).order_by(College.name).all()
    return {
        "status": "success",
        "data": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "description": c.short_description,
                "logo": c.logo_url,
                "color": c.theme_primary_color,
            }
            for c in colleges
        ]
    }


@router.get("/colleges/{college_id}")
def get_college_details(college_id: int, db: Session = Depends(get_db)):
    """
    Get college with key stats and information for display.
    """
    college = db.query(College).filter(College.id == college_id, College.is_active == True).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Get related data
    courses = db.query(Course).filter(Course.college_id == college_id, Course.is_active == True).all()
    faculty = db.query(Faculty).filter(Faculty.college_id == college_id, Faculty.is_active == True).all()
    placements = db.query(Placement).filter(Placement.college_id == college_id).all()
    facilities = db.query(Facility).filter(Facility.college_id == college_id).all()
    activities = db.query(Activity).filter(Activity.college_id == college_id).all()
    admission = db.query(Admission).filter(Admission.college_id == college_id).first()
    
    return {
        "status": "success",
        "data": {
            "id": college.id,
            "name": college.name,
            "slug": college.slug,
            "description": college.short_description,
            "logo": college.logo_url,
            "theme_color": college.theme_primary_color,
            "stats": {
                "courses": len(courses),
                "faculty": len(faculty),
                "facilities": len(facilities),
                "events": len(activities),
            },
            "courses": [
                {
                    "id": c.id,
                    "name": c.name,
                    "slug": c.slug,
                    "level": c.level,
                    "department": c.department,
                }
                for c in courses[:10]  # Limit to 10
            ],
            "faculty": [
                {
                    "id": f.id,
                    "name": f.name,
                    "designation": f.designation,
                    "photo": f.photo_url,
                }
                for f in faculty[:8]  # Limit to 8
            ],
            "facilities": [
                {
                    "id": f.id,
                    "name": f.name,
                    "image": f.image_url,
                }
                for f in facilities[:6]
            ],
            "placements": {
                "latest_year": placements[0].year if placements else None,
                "highest_package": placements[0].highest_package if placements else None,
                "average_package": placements[0].average_package if placements else None,
                "placement_percentage": placements[0].placement_percentage if placements else None,
            } if placements else {},
            "admission": {
                "procedure": admission.procedure_text,
                "eligibility": admission.eligibility_text,
            } if admission else {},
        }
    }


# =====================================
# PAGES - Public Routes
# =====================================

@router.get("/pages")
def list_pages(
    college_id: Optional[int] = Query(None),
    page_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get all active pages, optionally filtered by college and/or page type.
    """
    q = db.query(Page).filter(Page.is_active == True)
    
    if college_id:
        q = q.filter(Page.college_id == college_id)
    
    if page_type:
        q = q.filter(Page.page_type == page_type)
    
    pages = q.order_by(Page.title).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "college_id": p.college_id,
                "page_type": p.page_type,
                "template_type": p.template_type,
            }
            for p in pages
        ]
    }


@router.get("/pages/{page_id}")
def get_page_details(page_id: int, db: Session = Depends(get_db)):
    """
    Get detailed page content including sections and SEO metadata.
    Clean, simple response optimized for frontend rendering.
    """
    page = db.query(Page).filter(Page.id == page_id, Page.is_active == True).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Get sections
    sections = db.query(PageSection).filter(PageSection.page_id == page_id, PageSection.is_active == True).order_by(PageSection.sort_order).all()
    
    # Get SEO metadata
    seo = db.query(SEOMeta).filter(SEOMeta.page_id == page_id).first()
    
    # Get college info
    college = db.query(College).filter(College.id == page.college_id).first() if page.college_id else None
    
    # Build clean sections response
    sections_data = []
    for section in sections:
        items = db.query(SectionItem).filter(SectionItem.section_id == section.id).order_by(SectionItem.sort_order).all()
        
        # Clean section data - only essential fields
        section_obj = {
            "id": section.id,
            "type": section.section_type,
            "title": section.section_title,
            "subtitle": section.section_subtitle,
            "description": section.section_description,
            "background_image": section.background_image,
            "background_color": section.background_color,
            "items": [
                {
                    "id": i.id,
                    "title": i.title,
                    "description": i.description,
                    "image_url": i.image_url,
                    "cta_text": i.cta_text,
                    "cta_link": i.cta_link,
                }
                for i in items
            ]
        }
        
        # Add extra_data only if present
        if section.extra_data:
            section_obj["extra_data"] = section.extra_data
            
        sections_data.append(section_obj)
    
    # Clean page response
    return {
        "status": "success",
        "data": {
            "page": {
                "id": page.id,
                "title": page.title,
                "slug": page.slug,
                "college_id": page.college_id,
                "college_name": college.name if college else None,
            },
            "seo": {
                "title": seo.meta_title,
                "description": seo.meta_description,
                "url": seo.canonical_url,
                "image": seo.og_image,
            } if seo else {},
            "sections": sections_data,
        }
    }


# =====================================
# COURSES - Public Routes
# =====================================

@router.get("/courses")
def list_courses(
    college_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get courses list, optionally filtered by college.
    """
    q = db.query(Course).filter(Course.is_active == True)
    
    if college_id:
        q = q.filter(Course.college_id == college_id)
    
    courses = q.order_by(Course.name).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "college_id": c.college_id,
                "level": c.level,
                "department": c.department,
                "duration": c.duration,
                "fees": c.fees,
            }
            for c in courses
        ]
    }


@router.get("/courses/{course_id}")
def get_course_details(course_id: int, db: Session = Depends(get_db)):
    """
    Get course details with curriculum and career info.
    """
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    details = db.query(CoursePage).filter(CoursePage.course_id == course_id).first()
    college = db.query(College).filter(College.id == course.college_id).first() if course.college_id else None
    
    return {
        "status": "success",
        "data": {
            "id": course.id,
            "name": course.name,
            "slug": course.slug,
            "college_id": course.college_id,
            "college_name": college.name if college else None,
            "level": course.level,
            "department": course.department,
            "duration": course.duration,
            "fees": course.fees,
            "eligibility": course.eligibility,
            "overview": course.overview,
            "curriculum": details.curriculum if details else None,
            "career_opportunities": details.career_opportunities if details else None,
            "admission_process": details.admission_process if details else None,
        }
    }


# =====================================
# FACULTY - Public Routes
# =====================================

@router.get("/faculty")
def list_faculty(
    college_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get faculty members for college display.
    """
    q = db.query(Faculty).filter(Faculty.is_active == True)
    
    if college_id:
        q = q.filter(Faculty.college_id == college_id)
    
    faculty = q.order_by(Faculty.name).limit(20).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": f.id,
                "name": f.name,
                "college_id": f.college_id,
                "designation": f.designation,
                "photo": f.photo_url,
            }
            for f in faculty
        ]
    }


@router.get("/faculty/{faculty_id}")
def get_faculty_details(faculty_id: int, db: Session = Depends(get_db)):
    """
    Get faculty member profile.
    """
    member = db.query(Faculty).filter(Faculty.id == faculty_id, Faculty.is_active == True).first()
    if not member:
        raise HTTPException(status_code=404, detail="Faculty member not found")
    
    college = db.query(College).filter(College.id == member.college_id).first() if member.college_id else None
    
    return {
        "status": "success",
        "data": {
            "id": member.id,
            "name": member.name,
            "college_id": member.college_id,
            "college_name": college.name if college else None,
            "designation": member.designation,
            "qualification": member.qualification,
            "photo": member.photo_url,
            "bio": member.bio,
        }
    }


# =====================================
# PLACEMENTS - Public Routes
# =====================================

@router.get("/placements")
def list_placements(
    college_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get placement statistics.
    """
    q = db.query(Placement)
    
    if college_id:
        q = q.filter(Placement.college_id == college_id)
    
    placements = q.order_by(Placement.year.desc()).limit(5).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": p.id,
                "college_id": p.college_id,
                "year": p.year,
                "highest": p.highest_package,
                "average": p.average_package,
                "percentage": p.placement_percentage,
            }
            for p in placements
        ]
    }


@router.get("/placements/{placement_id}")
def get_placement_details(placement_id: int, db: Session = Depends(get_db)):
    """
    Get placement record details.
    """
    placement = db.query(Placement).filter(Placement.id == placement_id).first()
    if not placement:
        raise HTTPException(status_code=404, detail="Placement record not found")
    
    college = db.query(College).filter(College.id == placement.college_id).first()
    
    return {
        "status": "success",
        "data": {
            "id": placement.id,
            "college_id": placement.college_id,
            "college_name": college.name if college else None,
            "year": placement.year,
            "highest": placement.highest_package,
            "average": placement.average_package,
            "percentage": placement.placement_percentage,
        }
    }


# =====================================
# FACILITIES - Public Routes
# =====================================

@router.get("/facilities")
def list_facilities(
    college_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get facilities for display.
    """
    q = db.query(Facility)
    
    if college_id:
        q = q.filter(Facility.college_id == college_id)
    
    facilities = q.limit(12).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": f.id,
                "name": f.name,
                "description": f.description,
                "image": f.image_url,
            }
            for f in facilities
        ]
    }


@router.get("/facilities/{facility_id}")
def get_facility_details(facility_id: int, db: Session = Depends(get_db)):
    """
    Get facility information.
    """
    facility = db.query(Facility).filter(Facility.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    college = db.query(College).filter(College.id == facility.college_id).first()
    
    return {
        "status": "success",
        "data": {
            "id": facility.id,
            "name": facility.name,
            "description": facility.description,
            "image": facility.image_url,
            "college_name": college.name if college else None,
        }
    }


# =====================================
# ACTIVITIES - Public Routes
# =====================================

@router.get("/activities")
def list_activities(
    college_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get recent activities/events.
    """
    q = db.query(Activity)
    
    if college_id:
        q = q.filter(Activity.college_id == college_id)
    
    activities = q.order_by(Activity.event_date.desc()).limit(20).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": a.id,
                "title": a.title,
                "type": a.type,
                "description": a.description,
                "image": a.image_url,
                "date": a.event_date.isoformat() if a.event_date else None,
            }
            for a in activities
        ]
    }


@router.get("/activities/{activity_id}")
def get_activity_details(activity_id: int, db: Session = Depends(get_db)):
    """
    Get activity details.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    college = db.query(College).filter(College.id == activity.college_id).first()
    
    return {
        "status": "success",
        "data": {
            "id": activity.id,
            "title": activity.title,
            "type": activity.type,
            "description": activity.description,
            "image": activity.image_url,
            "date": activity.event_date.isoformat() if activity.event_date else None,
            "college_name": college.name if college else None,
        }
    }


# =====================================
# APPLICATIONS & ENQUIRIES - Public Routes
# =====================================

@router.post("/applications/submit")
def submit_application(
    request: ApplicationSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a new application.
    """
    # Validate college exists
    college = db.query(College).filter(College.id == request.college_id).first()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    # Validate course if provided
    if request.course_id:
        course = db.query(Course).filter(Course.id == request.course_id, Course.college_id == request.college_id).first()
        if not course:
            raise HTTPException(status_code=400, detail="Course not found for this college")
    
    # Create application
    application = Application(
        college_id=request.college_id,
        name=request.name,
        email=request.email,
        phone=request.phone,
        course_id=request.course_id,
        documents=request.documents,
        status="pending",
        created_at=datetime.utcnow(),
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return {
        "status": "success",
        "message": "Application submitted successfully",
        "data": {
            "id": application.id,
            "status": application.status,
        }
    }


@router.post("/enquiries/submit")
def submit_enquiry(
    request: EnquirySubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a new enquiry.
    """
    # Validate college if provided
    if request.college_id:
        college = db.query(College).filter(College.id == request.college_id).first()
        if not college:
            raise HTTPException(status_code=404, detail="College not found")
    
    # Create enquiry
    enquiry = Enquiry(
        college_id=request.college_id,
        name=request.name,
        email=request.email,
        phone=request.phone,
        message=request.message,
        created_at=datetime.utcnow(),
    )
    
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)
    
    return {
        "status": "success",
        "message": "Enquiry submitted successfully",
        "data": {
            "id": enquiry.id,
        }
    }


# =====================================
# SEARCH & FILTERS - Public Routes
# =====================================

@router.get("/search")
def search(
    query: str = Query(..., min_length=2),
    search_type: Optional[str] = Query(None),  # colleges, pages, courses, faculty
    db: Session = Depends(get_db)
):
    """
    Global search across colleges, pages, and courses.
    """
    results = {
        "status": "success",
        "query": query,
        "results": {}
    }
    
    # Search colleges
    if not search_type or search_type == "colleges":
        colleges = db.query(College).filter(
            College.is_active == True,
            (College.name.ilike(f"%{query}%") | College.short_description.ilike(f"%{query}%"))
        ).limit(10).all()
        results["results"]["colleges"] = [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "short_description": c.short_description,
            }
            for c in colleges
        ]
    
    # Search pages
    if not search_type or search_type == "pages":
        pages = db.query(Page).filter(
            Page.is_active == True,
            Page.title.ilike(f"%{query}%")
        ).limit(10).all()
        results["results"]["pages"] = [
            {
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "college_id": p.college_id,
            }
            for p in pages
        ]
    
    # Search courses
    if not search_type or search_type == "courses":
        courses = db.query(Course).filter(
            Course.is_active == True,
            (Course.name.ilike(f"%{query}%") | Course.overview.ilike(f"%{query}%"))
        ).limit(10).all()
        results["results"]["courses"] = [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "college_id": c.college_id,
            }
            for c in courses
        ]
    
    # Search faculty
    if not search_type or search_type == "faculty":
        faculty = db.query(Faculty).filter(
            Faculty.is_active == True,
            (Faculty.name.ilike(f"%{query}%") | Faculty.designation.ilike(f"%{query}%"))
        ).limit(10).all()
        results["results"]["faculty"] = [
            {
                "id": f.id,
                "name": f.name,
                "designation": f.designation,
                "college_id": f.college_id,
            }
            for f in faculty
        ]
    
    return results
