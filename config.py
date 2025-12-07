import os
from dotenv import load_dotenv

load_dotenv()  # loads the .env file

DATABASE_URL = os.getenv('DATABASE_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
URL_ENDPOINT = os.getenv('URL_ENDPOINT')
