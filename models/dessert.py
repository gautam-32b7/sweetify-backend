from sqlalchemy import Column, String, Float

from database import Base


# SQLAlchemy model representing a dessert in the database
class Dessert(Base):
    __tablename__ = 'desserts'

    id = Column(String, primary_key=True, index=True)
    dessert_name = Column(String)
    description = Column(String)
    price = Column(Float)
    image_url = Column(String)
