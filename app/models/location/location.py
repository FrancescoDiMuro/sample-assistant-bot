from datetime import datetime, UTC
from models.base.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4


class Location(Base):

    __tablename__ = "locations"
    
    # About "default" parameter:
    # https://docs.sqlalchemy.org/en/20/faq/
    # ormconfiguration.html#part-two-using-dataclasses-support-with-mappedasdataclass
    id: Mapped[UUID] = mapped_column(primary_key=True, nullable=False, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(nullable=True, onupdate=datetime.now(UTC))

    # These are the relationships between other models
    # Thanks to these variables, we can access the specified models
    # through this (Location) model
    user = relationship("User", back_populates="location")
