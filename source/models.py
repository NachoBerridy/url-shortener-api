# from source.database import Base
from database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, Boolean, ForeignKey


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String, index=True)
    short_url = Column(String, index=True)
    clicks = Column(Integer, default=0)
    user = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String)
    full_name = Column(String)
    email = Column(String)
    disabled = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )
