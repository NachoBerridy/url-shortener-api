from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# from source import urls
import routes.urls as urls

# from source import users
import routes.users as users

# import source.models as models
import services.database.models as models

# from source.database import engine, get_db
from services.database.database import engine as url_engine, get_db as url_get_db
from services.users_db.database import engine as user_engine


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
    # get the long url from the database
    db = next(url_get_db())
    url = db.query(models.URL).filter(models.URL.short_url == short_url).first()
    if url:
        url.clicks += 1
        db.commit()
        return RedirectResponse(url.long_url)  # Usar RedirectResponse para redirigir
    return {"error": "URL not found"}


app.include_router(urls.router)
app.include_router(users.router)
