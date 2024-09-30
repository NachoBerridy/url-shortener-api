from typing import List
from fastapi import Depends, status, APIRouter
from source import models
from source import schemas
from source.database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/url",
    tags=["URLs"],
)


@router.get("/", response_model=List[schemas.URLCreate])
def test_url(db: Session = Depends(get_db)):
    urls = db.query(models.URL).all()
    return urls


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.URLCreate)
def create_url(url: schemas.URLCreate, db: Session = Depends(get_db)):
    new_url = models.URL(**url.model_dump())
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url
