from database.db import SessionLocal
from models.todo.todo import Todo
from uuid import UUID


def create_todo(todo_data: dict) -> UUID:

    # Context manager for the SessionLocal
    # It opens a session with the db,
    # which is immediately closed after completing
    # all the operations in the context manager
    with SessionLocal() as session:

        # Create the record
        todo = Todo(**todo_data)

        # Add the record to the session
        session.add(todo)

        # Commit the session changes
        session.commit()

        # Return the record id
        return todo.id