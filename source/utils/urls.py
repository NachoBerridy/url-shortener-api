from services.database.models import URL
from sqlalchemy.orm import Session
import base64


def get_short_url(long_url: str):
    return base64.urlsafe_b64encode(long_url.encode()).decode()[:6]


def check_url_exists(short_url: str, db: Session) -> bool:
    url = db.query(URL).filter(URL.short_url == short_url).first()
    if url:
        return True
    return False
