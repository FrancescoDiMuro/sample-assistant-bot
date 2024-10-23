from database.db import SessionLocal
from models.reminder.reminder import Reminder
from uuid import UUID


def create_reminder(reminder_data: dict) -> UUID:

    # Context manager for the SessionLocal
    # It opens a session with the db,
    # which is immediately closed after completing
    # all the operations in the context manager
    with SessionLocal() as session:

        # Create the record
        reminder = Reminder(**reminder_data)

        # Add the record to the session
        session.add(reminder)

        # Commit the session changes
        session.commit()

        # Return the record id
        return reminder.id