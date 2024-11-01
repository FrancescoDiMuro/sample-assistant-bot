from database.db import SessionLocal
from models.todo.todo import Todo
from uuid import UUID


def delete_todo(todo_id: dict) -> UUID:

    # Context manager for the SessionLocal
    # It opens a session with the db,
    # which is immediately closed after completing
    # all the operations in the context manager
    with SessionLocal() as session:

        # Get the record
        todo = session.get(entity=Todo, ident=todo_id)

        # Delete the record
        session.delete(todo)
        
        # Commit the session changes
        session.commit()

        # Return the record id
        return todo_id