from datetime import datetime, UTC
from models.base.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from uuid import UUID, uuid4


class User(Base):

    __tablename__ = "users"
    
    # About "default" parameter:
    # https://docs.sqlalchemy.org/en/20/faq/
    # ormconfiguration.html#part-two-using-dataclasses-support-with-mappedasdataclass
    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False, default=uuid4)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(nullable=True, onupdate=datetime.now(UTC))

    # These are the relationships between other models
    # Thanks to these variables, we can access the specified models
    # through this (User) model
    location = relationship("Location", back_populates="user", lazy="joined", uselist=False)
    reminders = relationship("Reminder", back_populates="user")


    @hybrid_property
    def has_location(self):

        return len(self.location) > 0


