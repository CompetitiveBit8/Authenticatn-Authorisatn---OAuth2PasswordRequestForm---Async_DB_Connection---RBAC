from pydantic import BaseModel, EmailStr

#schema for new user
class UsersCreate(BaseModel):  
    username: str
    email: str
    password: str
    role: str

#schema for userlogin
class UserLogin(BaseModel):
    username: str
    password: str