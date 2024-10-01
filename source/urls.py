from typing import List
from fastapi import Depends, status, APIRouter, Request
from source import models
from source import schemas
from source.database import get_db
from sqlalchemy.orm import Session
import base64


router = APIRouter(
    prefix="/url",
    tags=["URLs"],
)


def get_short_url(long_url: str):
    return base64.urlsafe_b64encode(long_url.encode()).decode()[:6]


@router.get("/", response_model=List[schemas.URLCreate])
def test_url(db: Session = Depends(get_db)):
    urls = db.query(models.URL).all()
    return urls


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.URLCreate)
def create_url(url: schemas.URLCreate, request: Request, db: Session = Depends(get_db)):
    clicks = 0
    domain = request.base_url
    short_url = domain + "/" + get_short_url(url.long_url)
    new_url = models.URL(**url.model_dump(), short_url=short_url, clicks=clicks)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url
