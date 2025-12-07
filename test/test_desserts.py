from fastapi.testclient import TestClient
from starlette import status

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import pytest

from database import Base
from models.dessert import Dessert
from routers.desserts import get_session
from main import app

DATABASE_URL = 'sqlite:///./test_db.db'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

testing_local_session = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


# Override get_session
def override_get_session():
    session = testing_local_session()
    try:
        yield session
    finally:
        session.close()


# Fixture: dessert model
@pytest.fixture
def test_dessert():
    dessert_model = Dessert(
        id='e8919dc6-305c-4db2-b8da-30c64e874704',
        dessert_name='Waffle with Berries',
        description='Crispy golden waffle topped with fresh mixed berries',
        price=362,
        image_url='https://ik.imagekit.io/psrcaqvky/waffle_6kr5MDkWi.jpg'
    )
    db = testing_local_session()
    db.add(dessert_model)
    db.commit()

    # After the test runs, delete all desserts to reset the database
    yield dessert_model
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM desserts;'))
        connection.commit()


app.dependency_overrides[get_session] = override_get_session


# ---------- TESTS ----------
client = TestClient(app)


# Test: Retrieve list of all desserts
def test_list_desserts(test_dessert):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id': 'e8919dc6-305c-4db2-b8da-30c64e874704',
        'dessert_name': 'Waffle with Berries',
        'description': 'Crispy golden waffle topped with fresh mixed berries',
        'price': 362,
        'image_url': 'https://ik.imagekit.io/psrcaqvky/waffle_6kr5MDkWi.jpg'
    }]
