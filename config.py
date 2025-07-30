import os
from dotenv import load_dotenv

if os.environ.get("RENDER") is None:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
