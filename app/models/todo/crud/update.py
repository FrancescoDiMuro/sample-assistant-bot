from sqlalchemy import Update, update
from database.db import SessionLocal
from models.todo.todo import Todo
from uuid import UUID


def update_todo(todo_id: UUID, todo_data: dict) -> UUID:

    # Context manager for the SessionLocal
    # It opens a session with the db,
    # which is immediately closed after completing
    # all the operations in the context manager
    with SessionLocal() as session:

        # Get the record
        todo = session.get(entity=Todo, ident=todo_id)

        # Update todo data
        sql_statement: Update = update(Todo) \
                                .where(Todo.id == todo_id) \
                                .values(**todo_data)
        
        return session.execute(sql_statement)
