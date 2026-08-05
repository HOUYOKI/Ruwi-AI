from sqlalchemy.orm import Session
from app.models import User
class UserRepository:
    @staticmethod
    def by_email(db:Session,email:str): return db.query(User).filter(User.email==email.lower(),User.is_deleted.is_(False)).first()
    @staticmethod
    def by_id(db:Session,user_id:str): return db.get(User,user_id)
