from pydantic import BaseModel


class URLBase(BaseModel):
    long_url: str
    short_url: str
    clicks: int

    class Config:
        orm_mode = True


class URLCreate(URLBase):
    class Config:
        orm_mode = True
