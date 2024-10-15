from typing import List
from fastapi import Depends, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from services.database.url_db.database import get_db
from sqlalchemy.orm import Session
from utils.urls import get_all, get_my_urls, create_url, url_exists, URLBase, URLCreate


router = APIRouter(
    prefix="/url",
    tags=["URLs"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/all", response_model=List[URLCreate])
async def get_all_urls(db: Session = Depends(get_db)):
    return get_all(db)


@router.get("/me", response_model=List[URLCreate])
async def get_user_urls(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    return await get_my_urls(token, db)


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=URLCreate)
async def create_url_endpoint(
    url: URLBase,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    return await create_url(url, token, db)


@router.get("/url_exists")
async def url_exists_endpoint(short_url: str, db: Session = Depends(get_db)):
    return url_exists(short_url, db)
