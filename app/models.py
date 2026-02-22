from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from auth_database import Base

class Users(Base):
    __tablename__ = "users"

    id : Mapped [int] = mapped_column(primary_key=True, index=True)
    username : Mapped [str] = mapped_column(unique=False, index=True)
    email : Mapped [str] = mapped_column(index=True)
    password : Mapped [str] = mapped_column(index=True)
    # age: Mapped [int] = mapped_column(index=True)
    # address : Mapped [str] = mapped_column(index=True)
    role : Mapped [str] = mapped_column(index=True)
