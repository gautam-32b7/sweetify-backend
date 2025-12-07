from fastapi import FastAPI
from starlette import status

from database import engine
from models import dessert
from routers import desserts


app = FastAPI()


dessert.Base.metadata.create_all(bind=engine)


# Healthy endpoist (For testing purpose)
@app.get('/healthy', status_code=status.HTTP_200_OK)
async def health_check():
    return {'status': 'healthy'}


app.include_router(desserts.router)
