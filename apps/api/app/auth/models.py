"""User ORM model — maps fastapi-users to the existing kamari.app_users table."""
import uuid

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    # SQLAlchemyBaseUserTableUUID provides: id, email, hashed_password,
    # is_active, is_superuser, is_verified.
    __tablename__ = "app_users"
    __table_args__ = {"schema": "kamari"}

    role: Mapped[str] = mapped_column(String, default="member", nullable=False)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
