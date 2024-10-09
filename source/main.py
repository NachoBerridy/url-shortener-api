from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from source import urls
import routes.urls as urls

# from source import users
import routes.users as users

# import source.models as models
import services.database.models as models

# from source.database import engine, get_db
from services.database.database import engine, get_db


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Hello World", "documentation": " "}


@app.get("/{short_url}")
def redirect(short_url: str):
    # get the long url from the database
    db = next(get_db())
    url = db.query(models.URL).filter(models.URL.short_url == short_url).first()
    if url:
        url.clicks += 1
        db.commit()
        return {"url": url.long_url}
    return {"error": "URL not found"}


app.include_router(urls.router)
app.include_router(users.router)
