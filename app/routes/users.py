from fastapi import APIRouter, Depends, Security, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.jwt import create_access_token, verify_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


from pydantic import BaseModel,EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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


@router.post("/createUser")
def create_user(user: UserCreate, db: Session = Depends(get_db),  Response = None):
    # set_cors_headers(response)
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
def login(payload: LoginRequest, db: Session = Depends(get_db), Response = None):
    # set_cors_headers(response)

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}




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

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user), response: Response = None):
    # set_cors_headers(response)
    return {"name": current_user.name, "email": current_user.email, "message": "You are authenticated!"}

# user can change his password
@router.patch("/changepassword")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    response: Response = None,
):
    if not verify_password(current_password, current_user.password):
        raise HTTPException(status_code=401, detail="Invalid current password")

    if len(new_password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 characters)")

    current_user.password = hash_password(new_password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Password updated successfully"}

