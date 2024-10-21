from datetime import datetime, UTC
from models.base.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4


class Todo(Base):

    __tablename__ = "todos"
    
    # About "default" parameter:
    # https://docs.sqlalchemy.org/en/20/faq/
    # ormconfiguration.html#part-two-using-dataclasses-support-with-mappedasdataclass
    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    details: Mapped[str] = mapped_column(nullable=False)
    due_date: Mapped[datetime] = mapped_column(nullable=False)
    utc_offset: Mapped[int] = mapped_column(nullable=False)
    done: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(nullable=True, onupdate=datetime.now(UTC))

    # These are the relationships between other models
    # Thanks to these variables, we can access the specified models
    # through this (Todo) model
    user = relationship("User", back_populates="todos")
