from database.db import SessionLocal
from models.reminder.reminder import Reminder
from sqlalchemy import Select, select
from uuid import UUID


def retrieve_reminders() -> Reminder | None:

    with SessionLocal() as session:

        sql_statement: Select = select(Reminder)
        
        return session.scalars(sql_statement).all()


def retrieve_reminder(reminder_id: UUID) -> Reminder | None:

    with SessionLocal() as session:

        sql_statement: Select = select(Reminder) \
                                .where(Reminder.id == reminder_id)
        
        return session.scalar(sql_statement)
