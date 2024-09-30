from fastapi import FastAPI
from source import urls
import source.models as models
from source.database import engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(urls.router)
