from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Users
from utils import verify_password, hash_password
from auth_database import Base, get_db, engine
from schemas import UsersCreate, UserLogin
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer


SECRET_KEY = "aTS6vQE5KZ_cRoB2qKqiPznajl4EPFkOTILJyLUUkx0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY_MINUTES = 30


#major function that takes user data
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

app = FastAPI()

# main.py
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/signup")
async def register_user(user: UsersCreate, db: AsyncSession = Depends(get_db)):

    # check if the user exists or not
    stmnt = select(Users).where(Users.username == user.username)
    result = await db.execute(stmnt)
    existing_user = result.scalars().first()


    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    #hash the password
    hashed_password = hash_password(user.password)    
    
    #create nue user instance
    new_user = Users(
        username = user.username,
        email = user.email,
        password = hashed_password,
        role = user.role
        )
    
    #save user in databse
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    #return the value (excluding password)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email, "role": new_user.role}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    stmnt = select(Users).where(Users.username == form_data.username)
    result = await db.execute(stmnt)
    user_info = result.scalar()

    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")
    if not verify_password(form_data.password, user_info.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    token_data = {"sub": user_info.username, "role": user_info.role}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credential",
                                          headers = {"www-Authenticate": "bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credential_exception

    except JWTError:
        raise credential_exception
    
    return {"username": username, "role": role}

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user["username"]} | You accessed a protected route"}

def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission")
        
        return current_user
    return role_checker

@app.get("/profile")
def profile(current_user: dict = Depends(require_roles(["user", "admin"]))):
    return{"message": f"Profile of {current_user["username"]} ({current_user["role"]})"}

@app.get("/user/dashboard")
def user_dashboard(curren_user: dict = Depends(require_roles(["user", "admin"]))):
    if curren_user.get("role") == "user":
        return {"message": "Welcome User"}
    elif curren_user.get("role") == "admin":
        return {"message": f"Welcome to the user dashboard, Admin"}
        


@app.get("/admin/dashboard")
def user_dashboard(curren_user: dict = Depends(require_roles(["admin"]))):
    return {"message": "Welcome Admin"}