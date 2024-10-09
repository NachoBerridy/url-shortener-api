from datetime import timedelta
from typing import Annotated

from fastapi import Depends, status, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext

# from source.database import get_db
from services.database.database import get_db

from sqlalchemy.orm import Session

# from source.models import User as UserInDB
from services.database.models import User as UserInDB

# from source.schemas import UserBase, UserGet
from services.database.schemas import UserBase, UserGet

import logging

from utils.users import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)


logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

SECRET_KEY = "c28f403e7ad697e1157782602adad8757be51d8d3f549bc4558a4fd5343fa34a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserGet)
async def read_users_me(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> UserBase:
    return current_user


@router.post("/signup")
async def create_user(user: UserBase, db: Session = Depends(get_db)):
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
