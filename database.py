import os

from dotenv import load_dotenv
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData

load_dotenv()
engine = create_async_engine(os.getenv('DB_CONN'), echo=True,poolclass=NullPool)

metadata = MetaData()