from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.middleware import CollegeResolverMiddleware
from app.api.v1.router import api_router
import logging
from starlette.middleware.sessions import SessionMiddleware

try:
    from app.api.v1 import admin as admin_module
except Exception as e:
    logging.exception("Failed to import admin module")
    admin_module = None

app = FastAPI(title=settings.APP_NAME)

# Mount static files for admin templates
app.mount("/static", StaticFiles(directory="templet/static"), name="static")

# Session middleware for simple admin login
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.add_middleware(CollegeResolverMiddleware)
app.include_router(api_router, prefix="/api/v1")

# Also expose the server-rendered admin UI at the root `/admin` path so
# visiting http://localhost:8000/admin works (in addition to /api/v1/admin).
if admin_module and hasattr(admin_module, "router"):
    app.include_router(admin_module.router, prefix="/admin")
else:
    if not admin_module:
        logging.warning("Admin module not available; /admin routes not mounted")


@app.get("/health")
def health():
    return {"status": "OK"}
