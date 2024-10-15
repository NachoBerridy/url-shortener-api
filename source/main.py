from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import routes.urls as urls
import routes.users as users
import services.database.models as models
from services.database.url_db.database import engine as url_engine, get_db as url_get_db
from services.database.users_db.database import engine as user_engine


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base_url.metadata.create_all(bind=url_engine)
models.Base_user.metadata.create_all(bind=user_engine)


@app.get("/")
def read_root():
    return {"message": "Hello World", "documentation": " "}


@app.get("/{short_url}")
def redirect(short_url: str):
    db = next(url_get_db())
    url = db.query(models.URL).filter(models.URL.short_url == short_url).first()
    if url:
        url.clicks += 1
        db.commit()
        return RedirectResponse(url.long_url)
    return {"error": "URL not found"}


app.include_router(urls.router)
app.include_router(users.router)
