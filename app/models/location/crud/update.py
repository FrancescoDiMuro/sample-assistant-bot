from sqlalchemy import Update, update
from database.db import SessionLocal
from models.location.location import Location
from uuid import UUID


def update_location(location_id: UUID, location_data: dict) -> UUID:

    # Context manager for the SessionLocal
    # It opens a session with the db,
    # which is immediately closed after completing
    # all the operations in the context manager
    with SessionLocal() as session:

        # Update location data
        sql_statement: Update = update(Location) \
                                .where(Location.id == location_id) \
                                .values(**location_data)
        
        session.execute(sql_statement)

        session.commit()

        return location_id
