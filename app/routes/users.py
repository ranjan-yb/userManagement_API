from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordBearer
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext
from fastapi import HTTPException

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.jwt import create_access_token, verify_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def hash_password(password: str):
    
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 characters)")
    return pwd_context.hash(password)

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def home():
    return {"message": "Welcome to the User Management API!"}



@router.post("/createUser")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    print(type(user.password), user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
        # password = user.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ✅ Verify password function
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    # 1. Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Verify password
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # 3. Return success (later you’d issue a JWT or session token)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     payload = verify_token(token)
#     if payload is None:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     email: str = payload.get("sub")
#     user = db.query(User).filter(User.email == email).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# @router.get("/me")
# def read_users_me(current_user: User = Depends(get_current_user)):
    return {"name": current_user.name, "email": current_user.email}





# THIS IS THE SIMPLE AND EASY WAY OF AUTHENTICATION
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    email: str = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"name": current_user.name, "email": current_user.email}