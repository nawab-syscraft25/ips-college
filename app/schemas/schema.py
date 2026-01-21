from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Float,
    Table,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base


# Association table for placement recruiters
placement_recruiters = Table(
    "placement_recruiters",
    Base.metadata,
    Column("placement_id", ForeignKey("placements.id", ondelete="CASCADE"), primary_key=True),
    Column("recruiter_id", ForeignKey("recruiters.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True,
)

# Association table to attach shared sections to pages (many-to-many)
page_shared_sections = Table(
    "page_shared_sections",
    Base.metadata,
    Column("page_id", ForeignKey("pages.id", ondelete="CASCADE"), primary_key=True),
    Column("shared_section_id", ForeignKey("shared_sections.id", ondelete="CASCADE"), primary_key=True),
    Column("sort_order", Integer, default=0),
    extend_existing=True,
)

# Import `College` from app.models so you can edit `app/models/college.py` and
# have Alembic/autogenerate pick up changes from that file.
from app.models.college import College  # noqa: F401


class Page(Base):
    __tablename__ = "pages"
    __table_args__ = (
        UniqueConstraint("college_id", "slug", name="uq_pages_college_slug"),
        Index("ix_pages_college_active", "college_id", "is_active"),
        Index("ix_pages_parent_id", "parent_page_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    # PAGE TYPES: HOME, ABOUT, COLLEGES, COURSES, FACULTY, PLACEMENTS, FACILITIES, ADMISSIONS, CONTACT, STATIC
    page_type: Mapped[str] = mapped_column(String(50), nullable=False, default="STATIC")
    # TEMPLATE TYPES: BLANK, HERO_SECTION, COURSES_LIST, FACULTY_LIST, PLACEMENTS, FACILITIES_LIST
    template_type: Mapped[str] = mapped_column(String(50), nullable=True)
    # For inheritance: parent page (when child college inherits from parent college)
    parent_page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="SET NULL"), nullable=True)
    # Whether this page can be inherited by child colleges
    is_inheritable: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    college = relationship("College", back_populates="pages")
    parent_page = relationship("Page", remote_side=[id], back_populates="inherited_pages")
    inherited_pages = relationship("Page", remote_side=[parent_page_id], back_populates="parent_page")
    seo = relationship("SEOMeta", back_populates="page", uselist=False, cascade="all, delete-orphan")
    sections = relationship("PageSection", back_populates="page", cascade="all, delete-orphan", order_by="PageSection.sort_order")
    # shared sections can be attached to multiple pages
    shared_sections = relationship(
        "SharedSection",
        secondary=page_shared_sections,
        back_populates="pages",
        order_by="page_shared_sections.c.sort_order",
    )
    
    @property
    def seo_meta(self):
        """Alias for seo relationship for backward compatibility"""
        return self.seo


class SEOMeta(Base):
    __tablename__ = "seo_meta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, unique=True)
    meta_title: Mapped[str] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str] = mapped_column(String(1024), nullable=True)
    meta_keywords: Mapped[str] = mapped_column(String(1024), nullable=True)
    canonical_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    og_title: Mapped[str] = mapped_column(String(255), nullable=True)
    og_description: Mapped[str] = mapped_column(String(1024), nullable=True)
    og_image: Mapped[str] = mapped_column(String(1024), nullable=True)
    schema_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    # Additional SEO fields
    focus_keyword: Mapped[str] = mapped_column(String(255), nullable=True)
    readability_score: Mapped[str] = mapped_column(String(50), nullable=True)  # good, okay, needs improvement
    seo_score: Mapped[int] = mapped_column(Integer, nullable=True)  # 0-100

    page = relationship("Page", back_populates="seo")


class PageSection(Base):
    __tablename__ = "page_sections"
    __table_args__ = (
        Index("ix_page_sections_page_sort", "page_id", "sort_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    # SECTION TYPES: HERO, ABOUT, STATS, COURSES, FACULTY, PLACEMENTS, FACILITIES, TESTIMONIALS, ACHIEVEMENTS, FAQ, FORM, MEDIA_GALLERY, TEXT, CARDS
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)
    section_title: Mapped[str] = mapped_column(String(255), nullable=True)
    section_subtitle: Mapped[str] = mapped_column(String(255), nullable=True)
    section_description: Mapped[str] = mapped_column(Text, nullable=True)
    section_link: Mapped[str] = mapped_column(String(1024), nullable=True)
    # Background configuration
    background_type: Mapped[str] = mapped_column(String(50), nullable=True, default="none")  # none, color, image, gradient
    background_color: Mapped[str] = mapped_column(String(20), nullable=True)
    background_image: Mapped[str] = mapped_column(String(1024), nullable=True)
    background_gradient: Mapped[str] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Extra data for type-specific fields (hero image, CTA, etc.)
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    page = relationship("Page", back_populates="sections")
    items = relationship("SectionItem", back_populates="section", cascade="all, delete-orphan", order_by="SectionItem.sort_order")


class SectionItem(Base):
    __tablename__ = "section_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("page_sections.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    subtitle: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    video_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    cta_text: Mapped[str] = mapped_column(String(255), nullable=True)
    cta_link: Mapped[str] = mapped_column(String(1024), nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    section = relationship("PageSection", back_populates="items")


class SharedSection(Base):
    __tablename__ = "shared_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)
    section_title: Mapped[str] = mapped_column(String(255), nullable=True)
    section_subtitle: Mapped[str] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # pages that include this shared section
    pages = relationship("Page", secondary=page_shared_sections, back_populates="shared_sections")
    items = relationship("SharedSectionItem", back_populates="section", cascade="all, delete-orphan", order_by="SharedSectionItem.sort_order")


class SharedSectionItem(Base):
    __tablename__ = "shared_section_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shared_section_id: Mapped[int] = mapped_column(ForeignKey("shared_sections.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    subtitle: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    video_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    cta_text: Mapped[str] = mapped_column(String(255), nullable=True)
    cta_link: Mapped[str] = mapped_column(String(1024), nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    section = relationship("SharedSection", back_populates="items")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("college_id", "slug", name="uq_courses_college_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=True)
    department: Mapped[str] = mapped_column(String(255), nullable=True)
    duration: Mapped[str] = mapped_column(String(255), nullable=True)
    fees: Mapped[str] = mapped_column(String(255), nullable=True)
    eligibility: Mapped[str] = mapped_column(Text, nullable=True)
    overview: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    college = relationship("College", back_populates="courses")
    details = relationship("CoursePage", back_populates="course", uselist=False, cascade="all, delete-orphan")


class CoursePage(Base):
    __tablename__ = "course_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, unique=True)
    curriculum: Mapped[dict] = mapped_column(JSON, nullable=True)
    career_opportunities: Mapped[str] = mapped_column(Text, nullable=True)
    admission_process: Mapped[str] = mapped_column(Text, nullable=True)

    course = relationship("Course", back_populates="details")


class Faculty(Base):
    __tablename__ = "faculty"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str] = mapped_column(String(255), nullable=True)
    qualification: Mapped[str] = mapped_column(String(255), nullable=True)
    photo_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    college = relationship("College", back_populates="faculty")


class Placement(Base):
    __tablename__ = "placements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    highest_package: Mapped[float] = mapped_column(Float, nullable=True)
    average_package: Mapped[float] = mapped_column(Float, nullable=True)
    placement_percentage: Mapped[float] = mapped_column(Float, nullable=True)

    student_placements = relationship("StudentPlacement", back_populates="placement", cascade="all, delete-orphan")
    recruiters = relationship("Recruiter", secondary=placement_recruiters, back_populates="placements")


class StudentPlacement(Base):
    __tablename__ = "student_placements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    placement_id: Mapped[int] = mapped_column(ForeignKey("placements.id", ondelete="CASCADE"), nullable=False)
    student_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=True)
    package: Mapped[float] = mapped_column(Float, nullable=True)

    placement = relationship("Placement", back_populates="student_placements")


class Recruiter(Base):
    __tablename__ = "recruiters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(1024), nullable=True)

    placements = relationship("Placement", secondary=placement_recruiters, back_populates="recruiters")


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    event_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=True)


class Admission(Base):
    __tablename__ = "admissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    procedure_text: Mapped[str] = mapped_column(Text, nullable=True)
    eligibility_text: Mapped[str] = mapped_column(Text, nullable=True)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    documents: Mapped[dict] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Enquiry(Base):
    __tablename__ = "enquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RecruiterIndustry(Base):
    __tablename__ = "recruiter_industries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="COLLEGE_ADMIN")
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True)


class MenuItem(Base):
    """
    CMS navigation tree to support:
    - Top-level: Home, About Us, Colleges, Placements, Activities, Facilities, Contact Us
    - Nested items: per-college entries, sub-pages, etc.
    """

    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=True)
    # main / footer / admin etc.
    location: Mapped[str] = mapped_column(String(50), nullable=False, default="main")
    # optional explicit URL override (otherwise derived from page / college)
    url: Mapped[str] = mapped_column(String(1024), nullable=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="SET NULL"), nullable=True)
    college_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Self-referential relationship for parent menu item
    parent: Mapped['MenuItem'] = relationship("MenuItem", remote_side=[id], foreign_keys=[parent_id], uselist=False)


class MediaAsset(Base):
    """
    Simple media library used by CMS pages/sections:
    - hero images, president photo, governing body photos
    - campus images, facility images, recruiter logos, etc.
    """

    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    alt_text: Mapped[str] = mapped_column(String(255), nullable=True)
    media_type: Mapped[str] = mapped_column(String(50), nullable=True)  # image / video / document
    meta: Mapped[dict] = mapped_column(JSON, nullable=True)