import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import MembershipRole

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ProjectMembership(Base):
    __tablename__ = "project_memberships"
    __table_args__ = (
        # A user can only have one membership row per project. Enforced at the
        # database level, not just in the service layer.
        UniqueConstraint("project_id", "user_id", name="uq_project_membership_project_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # native_enum=False stores role as VARCHAR + CHECK constraint instead of a
    # Postgres-native ENUM type, so it behaves identically on SQLite and
    # Postgres and doesn't require ALTER TYPE migrations to add a value later.
    role: Mapped[MembershipRole] = mapped_column(
        SAEnum(
            MembershipRole,
            name="membership_role",
            native_enum=False,
            create_constraint=True,
            length=20,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=MembershipRole.MEMBER,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="memberships")
