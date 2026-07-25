"""Create the initial scoped persistence schema.

This first greenfield revision is generated from the frozen Task 3 ORM metadata.
Do not edit the referenced model definitions without adding a follow-up revision.
"""

from collections.abc import Sequence

from alembic import op

from llm_wiki.db import models as _models
from llm_wiki.db.base import Base

revision: str = "0001_scoped_persistence"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=False)


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind(), checkfirst=False)
