from database.db import SessionLocal
from models.reminder.reminder import Reminder
from uuid import UUID


def delete_reminder(reminder_id: dict) -> UUID:

    # Context manager for the SessionLocal
    # It opens a session with the db,
    # which is immediately closed after completing
    # all the operations in the context manager
    with SessionLocal() as session:

        # Get the record
        reminder = session.get(entity=Reminder, ident=reminder_id)

        # Delete the record
        session.delete(reminder)
        
        # Commit the session changes
        session.commit()

        # Return the record id
        return reminder_id