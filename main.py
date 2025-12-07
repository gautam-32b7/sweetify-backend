from fastapi import FastAPI

from database import engine
from models import dessert
from routers import desserts


app = FastAPI()


dessert.Base.metadata.create_all(bind=engine)

app.include_router(desserts.router)
