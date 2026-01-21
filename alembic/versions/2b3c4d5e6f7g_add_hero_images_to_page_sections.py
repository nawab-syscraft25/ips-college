"""add hero_images to page_sections

Revision ID: 2b3c4d5e6f7g
Revises: 1a2b3c4d5e6f
Create Date: 2026-01-21 11:55:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7g'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('page_sections', sa.Column('hero_images', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('page_sections', 'hero_images')
