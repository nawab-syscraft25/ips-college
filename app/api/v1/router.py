from fastapi import APIRouter
from app.api.v1 import colleges, pages, courses

api_router = APIRouter()

api_router.include_router(colleges.router, prefix="/colleges", tags=["Colleges"])
api_router.include_router(pages.router, prefix="/pages", tags=["Pages"])
api_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
