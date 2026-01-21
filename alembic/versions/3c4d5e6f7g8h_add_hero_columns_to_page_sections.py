"""add hero dedicated columns to page_sections

Revision ID: 3c4d5e6f7g8h
Revises: 2b3c4d5e6f7g
Create Date: 2026-01-21 12:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c4d5e6f7g8h'
down_revision = '2b3c4d5e6f7g'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('page_sections', sa.Column('hero_image_url', sa.String(length=1024), nullable=True))
    op.add_column('page_sections', sa.Column('hero_cta_text', sa.String(length=255), nullable=True))
    op.add_column('page_sections', sa.Column('hero_cta_link', sa.String(length=1024), nullable=True))
    op.add_column('page_sections', sa.Column('hero_style', sa.String(length=50), nullable=True))
    op.add_column('page_sections', sa.Column('hero_text_color', sa.String(length=50), nullable=True))
    op.add_column('page_sections', sa.Column('hero_height', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('page_sections', 'hero_height')
    op.drop_column('page_sections', 'hero_text_color')
    op.drop_column('page_sections', 'hero_style')
    op.drop_column('page_sections', 'hero_cta_link')
    op.drop_column('page_sections', 'hero_cta_text')
    op.drop_column('page_sections', 'hero_image_url')
