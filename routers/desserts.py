from typing import Annotated
import os
import tempfile
import shutil
import uuid

from fastapi import APIRouter, Depends, Form, File, HTTPException, UploadFile
from starlette import status
from sqlalchemy.orm import Session

from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from database import session_local
from models.dessert import Dessert
from config import PRIVATE_KEY, PUBLIC_KEY, URL_ENDPOINT

router = APIRouter()


# Provide a database session and ensure it's closed after use
def get_session():
    session = session_local()
    try:
        yield session
    finally:
        session.close()


# Defines a dependency that provides a database session to routes
session_dep = Annotated[Session, Depends(get_session)]


# SDK initialization
imagekit = ImageKit(
    private_key=PRIVATE_KEY,
    public_key=PUBLIC_KEY,
    url_endpoint=URL_ENDPOINT
)


# Retrieve list of all desserts
@router.get('/', status_code=status.HTTP_200_OK)
async def list_desserts(session: session_dep):
    return session.query(Dessert).all()


# Retrieve a single dessert by its ID
@router.get('/desserts/{dessert_id}', status_code=status.HTTP_200_OK)
async def retrieve_dessert(session: session_dep, dessert_id: str):
    dessert = session.query(Dessert).filter(Dessert.id == dessert_id).first()
    if dessert is not None:
        return dessert
    raise HTTPException(status_code=404, detail='Dessert not found')


# Create a new dessert entry
@router.post('/create-dessert', status_code=status.HTTP_201_CREATED)
async def create_dessert(session: session_dep, dessert_name: str = Form(...), description: str = Form(...), price: float = Form(...), image: UploadFile = File(...)):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(image.file, temp_file)

            upload_result = imagekit.upload_file(
                file=open(temp_file_path, 'rb'),
                file_name=image.filename,
                options=UploadFileRequestOptions(
                    use_unique_file_name=True, tags=['image-upload'])
            )

            if upload_result.response_metadata.http_status_code == 200:
                dessert_model = Dessert(
                    id=uuid.uuid4(),
                    dessert_name=dessert_name,
                    description=description,
                    price=price,
                    image_url=upload_result.url
                )
                session.add(dessert_model)
                session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        image.file.close()


# Update an existing dessert by its ID
@router.put('/dessert/{dessert_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_dessert(session: session_dep, dessert_id: str, dessert_name: str = Form(...), description: str = Form(...), price: float = Form(...), image: UploadFile = File(...)):
    dessert = session.query(Dessert).filter(Dessert.id == dessert_id).first()
    if dessert is None:
        raise HTTPException(status_code=404, detail='Dessert not found')
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(image.file, temp_file)

            upload_result = imagekit.upload_file(
                file=open(temp_file_path, 'rb'),
                file_name=image.filename,
                options=UploadFileRequestOptions(
                    use_unique_file_name=True, tags=['image-upload'])
            )

            if upload_result.response_metadata.http_status_code == 200:
                dessert.dessert_name = dessert_name
                dessert.description = description
                dessert.price = price
                dessert.image_url = upload_result.url
                session.add(dessert)
                session.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        image.file.close()


# Delete a dessert by its ID
@router.delete('/dessert/{dessert_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_dessert(session: session_dep, dessert_id: str):
    dessert = session.query(Dessert).filter(Dessert.id == dessert_id).first()
    if dessert is None:
        raise HTTPException(status_code=404, detail='Dessert not found')
    session.query(Dessert).filter(Dessert.id == dessert_id).delete()
    session.commit()
