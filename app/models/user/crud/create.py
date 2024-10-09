from database.db import SessionLocal
from models.user.user import User
from uuid import UUID


def create_user(user_data: dict) -> UUID:

    # Context manager for the SessionLocal
    # It opens a session with the db,
    # which is immediately closed after completing
    # all the operations in the context manager
    with SessionLocal() as session:

        # Create the record
        user = User(**user_data)

        # Add the record to the session
        session.add(user)

        # Commit the session changes
        session.commit()

        # Return the record id
        return user.id