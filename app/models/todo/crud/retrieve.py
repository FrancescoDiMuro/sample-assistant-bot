from database.db import SessionLocal
from models.todo.todo import Todo
from sqlalchemy import Select, select


def retrieve_todos() -> Todo | None:

    with SessionLocal() as session:

        sql_statement: Select = select(Todo) \
                                .where(Todo.done.is_(False))
        
        return session.scalars(sql_statement).all()


def retrieve_todo(todo_id: int) -> Todo | None:

    with SessionLocal() as session:

        sql_statement: Select = select(Todo) \
                                .where(Todo.id == todo_id)
        
        return session.scalar(sql_statement)
