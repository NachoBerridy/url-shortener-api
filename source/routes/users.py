from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext

from services.users_db.database import get_db

from sqlalchemy.orm import Session
from services.database.models import User as UserInDB
from dotenv import load_dotenv
import os


import logging

from utils.users import (
    get_current_active_user,
    check_username_exists,
    check_email_exists,
    create_user,
    login_for_access_token,
    read_users_me,
)

load_dotenv()


# Schemas
class UserBase(BaseModel):
    username: str
    password: str
    full_name: str
    email: str

    class Config:
        orm_mode = True


class UserGet(UserBase):
    id: int

    class Config:
        orm_mode = True


logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_EXPIRATION")

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return login_for_access_token(form_data)


@router.get("/me", response_model=UserGet)
async def get_user(current_user: UserInDB = Depends(get_current_active_user)):
    return read_users_me(current_user)


@router.post("/signup")
async def signup(user: UserBase, db: Session = Depends(get_db)):
    return create_user(user, db)


@router.get("/email_exists")
async def email_exists(email: str, db: Session = Depends(get_db)):
    return check_email_exists(email, db)


@router.get("/username_exists")
async def username_exists(username: str, db: Session = Depends(get_db)):
    return check_username_exists(username, db)
