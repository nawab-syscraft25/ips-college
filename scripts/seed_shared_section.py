"""One-off script to create a demo SharedSection and items.

Run from project root in the same venv as the app:

    python scripts/seed_shared_section.py

It will create a SharedSection and two items if none exist.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so `import app` works when running this script directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import SessionLocal
from app.schemas.schema import SharedSection, SharedSectionItem


def seed():
    db = SessionLocal()
    try:
        existing = db.query(SharedSection).count()
        if existing:
            print(f"SharedSection table already has {existing} rows — nothing to do.")
            return

        sec = SharedSection(
            section_type="CAROUSEL",
            section_title="Demo Carousel",
            section_subtitle="Sample slides",
            sort_order=0,
            is_active=True,
        )
        db.add(sec)
        db.commit()
        db.refresh(sec)

        items = [
            SharedSectionItem(
                shared_section_id=sec.id,
                title="Slide One",
                subtitle="Welcome",
                description="First demo slide",
                image_url="https://via.placeholder.com/1200x400?text=Slide+1",
                sort_order=0,
            ),
            SharedSectionItem(
                shared_section_id=sec.id,
                title="Slide Two",
                subtitle="About Us",
                description="Second demo slide",
                image_url="https://via.placeholder.com/1200x400?text=Slide+2",
                sort_order=1,
            ),
        ]
        for it in items:
            db.add(it)
        db.commit()
        print("Created demo SharedSection and 2 items.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
