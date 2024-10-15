from datetime import datetime, timedelta, timezone
from typing import Annotated
import os
from dotenv import load_dotenv
import jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging
from services.database.users_db.database import get_db
from services.database.models import User as UserInDB

load_dotenv()


logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error veryfing password: {e}")
        return False


def get_user(username: str, db: Session) -> UserInDB | None:
    try:
        user = db.query(UserInDB).filter(UserInDB.username == username).first()
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None


def authenticate_user(username: str, password: str, db: Session) -> UserInDB | bool:
    user = get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta if expires_delta else timedelta(minutes=15)
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error al crear el token JWT: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError as e:
        logger.error(f"JWT Error: {e}")
        raise credentials_exception

    user = get_user(token_data.username, db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def check_username_exists(username: str, db: Session) -> bool:
    return db.query(UserInDB).filter(UserInDB.username == username).first() is not None


def check_email_exists(email: str, db: Session) -> bool:
    return db.query(UserInDB).filter(UserInDB.email == email).first() is not None


async def create_user(user: UserBase, db: Session = Depends(get_db)):
    try:
        if check_username_exists(user.username, db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The username already exists",
            )

        if check_email_exists(user.email, db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The email already exists",
            )

        db_user = UserInDB(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            password=get_password_hash(user.password),
            disabled=False,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        logger.error(f"Error trying to create user: {e}")
        raise HTTPException(status_code=500, detail="Error al crear el usuario")


async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        logger.warning(
            f"Falied login attempt for user: {form_data.username} at {datetime.now()}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def read_users_me(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> UserBase:
    return current_user
