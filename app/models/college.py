from sqlalchemy import Integer, String, Boolean, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.core.database import Base


class College(Base):
    __tablename__ = "colleges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    subdomain: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    logo_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    short_description: Mapped[str] = mapped_column(Text, nullable=True)
    theme_primary_color: Mapped[str] = mapped_column(String(20), nullable=True)
    theme_secondary_color: Mapped[str] = mapped_column(String(20), nullable=True)
    is_parent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    parent: Mapped["College"] = relationship("College", remote_side=[id], back_populates="children")
    children: Mapped[List["College"]] = relationship("College", back_populates="parent", cascade="all, delete-orphan")

    pages = relationship("Page", back_populates="college", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="college", cascade="all, delete-orphan")
    faculty = relationship("Faculty", back_populates="college", cascade="all, delete-orphan")
    
    def get_root_college(self):
        """Get the root (parent) college in the hierarchy"""
        if self.parent_id:
            return self.parent.get_root_college()
        return self
    
    def is_child(self):
        """Check if this is a child college"""
        return self.parent_id is not None
