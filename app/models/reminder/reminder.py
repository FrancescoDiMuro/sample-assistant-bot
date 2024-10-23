from datetime import datetime, UTC
from models.base.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4


class Reminder(Base):

    __tablename__ = "reminders"
    
    # About "default" parameter:
    # https://docs.sqlalchemy.org/en/20/faq/
    # ormconfiguration.html#part-two-using-dataclasses-support-with-mappedasdataclass
    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    todo_id: Mapped[UUID] = mapped_column(ForeignKey("todos.id"), nullable=False)
    remind_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now(UTC))

    # These are the relationships between other models
    # Thanks to these variables, we can access the specified models
    # through this (Todo) model
    todo = relationship("Todo", back_populates="reminder")
