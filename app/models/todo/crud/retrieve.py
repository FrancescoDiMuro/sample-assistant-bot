from uuid import UUID
from database.db import SessionLocal
from models.todo.todo import Todo
from sqlalchemy import Select, select


def retrieve_todos(is_done: bool = False) -> Todo | None:

    with SessionLocal() as session:

        sql_statement: Select = select(Todo) \
                                .where(Todo.done.is_(is_done)) \
                                .order_by(Todo.due_date)
        
        return session.scalars(sql_statement).all()


def retrieve_todo(todo_id: UUID) -> Todo | None:

    with SessionLocal() as session:

        sql_statement: Select = select(Todo) \
                                .where(Todo.id == todo_id)
        
        return session.scalar(sql_statement)
