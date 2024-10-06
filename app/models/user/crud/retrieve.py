from database.db import SessionLocal
from models.user.user import User
from sqlalchemy import Select, select


def retrieve_user(user_telegram_id: int) -> User | None:

    with SessionLocal() as session:

        sql_statement: Select = select(User) \
                                .where(User.telegram_id == user_telegram_id)
        
        return session.scalar(sql_statement)
