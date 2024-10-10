from source.services.database.models import URL
from sqlalchemy.orm import Session
import base64
from fastapi import Depends, status, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from services.database.url_db.database import get_db
from utils.users import get_current_user
from pydantic import BaseModel


class URLBase(BaseModel):
    long_url: str
    name: str

    class Config:
        orm_mode = True


class URLCreate(URLBase):
    short_url: str
    clicks: int
    name: str

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/url",
    tags=["URLs"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_short_url(long_url: str):
    return base64.urlsafe_b64encode(long_url.encode()).decode()[:6]


def check_url_exists(short_url: str, db: Session) -> bool:
    url = db.query(URL).filter(URL.short_url == short_url).first()
    if url:
        return True
    return False


def get_all(db: Session = Depends(get_db)):
    urls = db.query(URL).all()
    return urls


async def get_my_urls(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    user = await get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    urls = db.query(URL).filter(URL.user == user.id).all()
    return urls


async def create_url(
    url: URLBase,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user = await get_current_user(token, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    clicks = 0
    short_url = get_short_url(url.long_url)

    while check_url_exists(short_url, db):
        short_url = get_short_url(url.long_url)

    new_url = URL(
        long_url=url.long_url,
        short_url=short_url,
        clicks=clicks,
        user=user.id,
        name=url.name,
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url


async def url_exists(short_url: str, db: Session = Depends(get_db)):
    return check_url_exists(short_url, db)
