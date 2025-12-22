from datetime import datetime
import sys
from pathlib import Path

# Ensure the project root is on sys.path when running via pytest
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.models.college import College
from app.schemas.schema import (
    Page,
    PageSection,
    SectionItem,
    Course,
    CoursePage,
    Faculty,
    Placement,
    StudentPlacement,
    Recruiter,
    Activity,
    Facility,
    Admission,
    Application,
    Enquiry,
    MenuItem,
    MediaAsset,
)


SAMPLE_IMAGE = "https://www.gstatic.com/webp/gallery/1.webp"


def test_seed_sample_data():
    """
    Seed the database with a minimal but representative content tree that
    exercises most of the schema:

    - Global pages: Home, About Us, Colleges, Placements, Activities, Facilities, Contact Us
    - Colleges: IBMR, SOC, ISR, SoSS, COC, IOHM, COE, College of Law, IFT
    - For IBMR: courses, faculty, placements, activities, facilities, admissions, applications
    - Menus & media and basic sections for Home/About.

    Running this test multiple times should be safe (it is idempotent).
    """
    db = SessionLocal()
    try:
        # If we already have IBMR seeded, assume sample data exists.
        if db.query(College).filter_by(slug="ibmr").first():
            return

        # --- Colleges ---
        college_defs = [
            ("IBMR", "ibmr"),
            ("School of Computing (SOC)", "soc"),
            ("Institute of Science & Research (ISR)", "isr"),
            ("School of Social Sciences (SoSS)", "soss"),
            ("College of Commerce (COC)", "coc"),
            ("Institute of Hotel Management (IOHM)", "iohm"),
            ("College of Engineering (COE)", "coe"),
            ("College of Law", "law"),
            ("Institute of Fashion Technology (IFT)", "ift"),
        ]

        colleges = []
        for name, slug in college_defs:
            c = College(
                name=name,
                slug=slug,
                subdomain=slug,
                short_description=f"{name} at IPS Academy.",
                theme_primary_color="#004aad",
                theme_secondary_color="#ffb800",
                is_parent=(slug == "ibmr"),
            )
            db.add(c)
            colleges.append(c)
        db.commit()

        ibmr = next(c for c in colleges if c.slug == "ibmr")

        # --- Media ---
        hero_image = MediaAsset(
            file_url=SAMPLE_IMAGE,
            title="Campus Hero Banner",
            alt_text="IPS Academy campus",
            media_type="image",
            meta=None,
        )
        db.add(hero_image)
        db.commit()

        # --- Global pages (home, about, placements, activities, facilities, contact, colleges) ---
        home_page = Page(title="Home", slug="home", college_id=None)
        about_page = Page(title="About Us", slug="about", college_id=None)
        colleges_page = Page(title="Colleges", slug="colleges", college_id=None)
        placements_page = Page(title="Placements", slug="placements", college_id=None)
        activities_page = Page(title="Activities", slug="activities", college_id=None)
        facilities_page = Page(title="Facilities", slug="facilities", college_id=None)
        contact_page = Page(title="Contact Us", slug="contact-us", college_id=None)
        ibmr_page = Page(title="IBMR Home", slug="ibmr-home", college_id=ibmr.id)

        db.add_all(
            [
                home_page,
                about_page,
                colleges_page,
                placements_page,
                activities_page,
                facilities_page,
                contact_page,
                ibmr_page,
            ]
        )
        db.commit()

        # --- Home sections (banner, about, key numbers) ---
        home_banner = PageSection(
            page_id=home_page.id,
            section_type="HERO",
            section_title="Welcome to IPS Academy",
            section_subtitle="360° Campus View",
            sort_order=0,
        )
        home_about = PageSection(
            page_id=home_page.id,
            section_type="CONTENT",
            section_title="About IPS Academy",
            section_subtitle=None,
            sort_order=1,
        )
        home_numbers = PageSection(
            page_id=home_page.id,
            section_type="STATS",
            section_title="Key Numbers",
            section_subtitle=None,
            sort_order=2,
        )
        db.add_all([home_banner, home_about, home_numbers])
        db.commit()

        db.add_all(
            [
                SectionItem(
                    section_id=home_banner.id,
                    title="Explore Our Campus",
                    subtitle=None,
                    description="Immersive 360° campus experience.",
                    image_url=SAMPLE_IMAGE,
                    video_url=None,
                    cta_text="Apply Now",
                    cta_link="/apply",
                    sort_order=0,
                ),
                SectionItem(
                    section_id=home_about.id,
                    title="Multi-disciplinary Excellence",
                    subtitle=None,
                    description="IPS Academy is a leading institution offering UG, PG and Doctoral programs.",
                    sort_order=0,
                ),
                SectionItem(
                    section_id=home_numbers.id,
                    title="Students",
                    description="8000+",
                    sort_order=0,
                ),
                SectionItem(
                    section_id=home_numbers.id,
                    title="Faculty",
                    description="400+",
                    sort_order=1,
                ),
            ]
        )
        db.commit()

        # --- About Us sections: President Message & Governing Body ---
        about_president = PageSection(
            page_id=about_page.id,
            section_type="CONTENT",
            section_title="President Message",
            sort_order=0,
        )
        about_governing = PageSection(
            page_id=about_page.id,
            section_type="LIST",
            section_title="Governing Body",
            sort_order=1,
        )
        db.add_all([about_president, about_governing])
        db.commit()

        db.add(
            SectionItem(
                section_id=about_president.id,
                title="From the President's Desk",
                description="A message highlighting vision, values and commitment to holistic education.",
                image_url=SAMPLE_IMAGE,
                sort_order=0,
            )
        )
        db.add(
            SectionItem(
                section_id=about_governing.id,
                title="Chairperson",
                subtitle="Dr. A. Example",
                description="Provides strategic direction and oversight.",
                sort_order=0,
            )
        )
        db.commit()

        # --- Menus (main navigation) ---
        main_items = [
            MenuItem(title="Home", slug="home", location="main", page_id=home_page.id, sort_order=0),
            MenuItem(title="About Us", slug="about-us", location="main", page_id=about_page.id, sort_order=1),
            MenuItem(title="Colleges", slug="colleges", location="main", page_id=colleges_page.id, sort_order=2),
            MenuItem(title="Placements", slug="placements", location="main", page_id=placements_page.id, sort_order=3),
            MenuItem(title="Activities", slug="activities", location="main", page_id=activities_page.id, sort_order=4),
            MenuItem(title="Facilities", slug="facilities", location="main", page_id=facilities_page.id, sort_order=5),
            MenuItem(title="Contact Us", slug="contact-us", location="main", page_id=contact_page.id, sort_order=6),
        ]
        db.add_all(main_items)
        db.commit()

        # Child menu items for some colleges under "Colleges"
        colleges_root = next(m for m in main_items if m.slug == "colleges")
        for c in colleges:
            db.add(
                MenuItem(
                    title=c.name,
                    slug=c.slug,
                    location="main",
                    college_id=c.id,
                    parent_id=colleges_root.id,
                    sort_order=0,
                )
            )
        db.commit()

        # --- IBMR: courses and course pages ---
        ibmr_courses = [
            ("BBA", "bba", "UG"),
            ("MBA", "mba", "PG"),
            ("Ph.D (Management)", "phd-management", "PhD"),
        ]
        course_objects = []
        for name, slug, level in ibmr_courses:
            course = Course(
                college_id=ibmr.id,
                name=name,
                slug=slug,
                level=level,
                department="Management",
                duration="3 Years" if level == "UG" else "2 Years",
                fees="As per norms",
                eligibility="As per IPS Academy / university guidelines.",
                overview=f"{name} program at IBMR.",
            )
            db.add(course)
            db.commit()
            db.refresh(course)
            course_objects.append(course)
            db.add(
                CoursePage(
                    course_id=course.id,
                    curriculum={"semesters": 6},
                    career_opportunities="Corporate roles, entrepreneurship, higher studies.",
                    admission_process="Based on entrance test / merit as per regulations.",
                )
            )
            db.commit()

        # --- IBMR: faculty ---
        db.add_all(
            [
                Faculty(
                    college_id=ibmr.id,
                    name="Dr. Management Expert",
                    designation="Professor & Director",
                    qualification="Ph.D, MBA",
                    photo_url=SAMPLE_IMAGE,
                    bio="Leads the institute with 20+ years of academic and industry experience.",
                ),
                Faculty(
                    college_id=ibmr.id,
                    name="Prof. Business Mentor",
                    designation="Associate Professor",
                    qualification="MBA",
                    photo_url=SAMPLE_IMAGE,
                    bio="Specializes in marketing and corporate relations.",
                ),
            ]
        )
        db.commit()

        # --- IBMR: placements (stats, recruiter, student placements) ---
        placement = Placement(
            college_id=ibmr.id,
            year=datetime.utcnow().year,
            highest_package=24.0,
            average_package=6.5,
            placement_percentage=92.0,
        )
        db.add(placement)
        db.commit()
        db.refresh(placement)

        recruiter = Recruiter(
            name="TopCorp Ltd.",
            industry="IT Services",
            logo_url=SAMPLE_IMAGE,
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)

        db.add(StudentPlacement(placement_id=placement.id, student_name="John Doe", company_name="TopCorp Ltd.", package=12.0))
        db.commit()

        # associate recruiter with placement via relationship
        placement.recruiters.append(recruiter)
        db.add(placement)
        db.commit()

        # --- IBMR: activities (events, workshops, sports) ---
        db.add_all(
            [
                Activity(
                    college_id=ibmr.id,
                    type="Event",
                    title="Annual Fest",
                    description="Cultural and management events.",
                    image_url=SAMPLE_IMAGE,
                    event_date=datetime.utcnow(),
                ),
                Activity(
                    college_id=ibmr.id,
                    type="Workshop",
                    title="Industry 4.0 Workshop",
                    description="Hands-on sessions with industry experts.",
                    image_url=SAMPLE_IMAGE,
                    event_date=datetime.utcnow(),
                ),
                Activity(
                    college_id=ibmr.id,
                    type="Sports",
                    title="Inter-college Sports Meet",
                    description="Track and field, cricket, football.",
                    image_url=SAMPLE_IMAGE,
                    event_date=datetime.utcnow(),
                ),
            ]
        )
        db.commit()

        # --- IBMR: facilities ---
        db.add_all(
            [
                Facility(college_id=ibmr.id, name="Hostel", description="On-campus hostel with modern amenities.", image_url=SAMPLE_IMAGE),
                Facility(college_id=ibmr.id, name="Library", description="Rich collection of management and research books.", image_url=SAMPLE_IMAGE),
                Facility(college_id=ibmr.id, name="Wellness Centre", description="Health and counseling services for students.", image_url=SAMPLE_IMAGE),
            ]
        )
        db.commit()

        # --- IBMR: admissions & applications ---
        admission = Admission(
            college_id=ibmr.id,
            procedure_text="Step-by-step admission procedure for IBMR programs.",
            eligibility_text="Eligibility as per program and regulatory guidelines.",
        )
        db.add(admission)
        db.commit()

        sample_app = Application(
            college_id=ibmr.id,
            name="Sample Applicant",
            email="applicant@example.com",
            phone="9999999999",
            course_id=course_objects[0].id,
            documents={"resume": "uploaded"},
            status="Pending",
        )
        db.add(sample_app)
        db.commit()

        # --- Global contact enquiries ---
        enquiry = Enquiry(
            college_id=None,
            name="Prospective Student",
            email="student@example.com",
            phone="8888888888",
            message="I would like to know more about MBA admissions.",
        )
        db.add(enquiry)
        db.commit()

    finally:
        db.close()


