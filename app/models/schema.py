
"""
Compatibility shim: re-export models from `app.schemas.schema`.
The canonical models live in `app/schemas/schema.py`.
"""

from app.schemas.schema import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("__")]
