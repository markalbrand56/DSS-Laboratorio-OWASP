from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    public_key_RSA = Column(String, nullable=True)
    public_key_ECC = Column(String, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
