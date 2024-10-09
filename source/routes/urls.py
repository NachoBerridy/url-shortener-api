from typing import List
from fastapi import Depends, status, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer

# from source.models import URL
from services.database.models import URL

# from source import schemas
import services.database.schemas as schemas

# from source.database import get_db

from services.database.database import get_db

from sqlalchemy.orm import Session
import base64

# from source.users import get_current_user
from utils.users import get_current_user


router = APIRouter(
    prefix="/url",
    tags=["URLs"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_short_url(long_url: str):
    return base64.urlsafe_b64encode(long_url.encode()).decode()[:6]


@router.get("/all", response_model=List[schemas.URLCreate])
def test_url(db: Session = Depends(get_db)):
    urls = db.query(URL).all()
    return urls


@router.get("/me", response_model=List[schemas.URLCreate])
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


@router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=schemas.URLCreate
)
async def create_url(
    url: schemas.URLBase,
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
