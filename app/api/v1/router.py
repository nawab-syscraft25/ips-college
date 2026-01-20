from fastapi import APIRouter

api_router = APIRouter()

# Try importing and including optional sub-routers if present.
try:
	from app.api.v1 import colleges
except Exception:
	colleges = None

try:
	from app.api.v1 import pages
except Exception:
	pages = None

try:
	from app.api.v1 import courses
except Exception:
	courses = None

try:
	from app.api.v1 import admin
except Exception:
	admin = None

try:
	from app.api.v1 import public
except Exception:
	public = None

if colleges and hasattr(colleges, "router"):
	api_router.include_router(colleges.router, prefix="/colleges", tags=["Colleges"])

if pages and hasattr(pages, "router"):
	api_router.include_router(pages.router, prefix="/pages", tags=["Pages"])

if courses and hasattr(courses, "router"):
	api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])

if admin and hasattr(admin, "router"):
	api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

if public and hasattr(public, "router"):
	api_router.include_router(public.router, prefix="", tags=["Public API"])
