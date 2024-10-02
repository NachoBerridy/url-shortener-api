from pydantic import BaseModel


class URLBase(BaseModel):
    long_url: str

    class Config:
        orm_mode = True


class URLCreate(URLBase):
    short_url: str
    clicks: int

    class Config:
        orm_mode = True


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
