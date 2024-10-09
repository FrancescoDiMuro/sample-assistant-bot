from database.db import SessionLocal
from models.location.location import Location
from uuid import UUID


def create_location(location_data: dict) -> UUID:

    # Context manager for the SessionLocal
    # It opens a session with the db,
    # which is immediately closed after completing
    # all the operations in the context manager
    with SessionLocal() as session:

        # Create the record
        location = Location(**location_data)

        # Add the record to the session
        session.add(location)

        # Commit the session changes
        session.commit()

        # Return the record id
        return location.id