import os 
import asyncio
from dotenv import load_dotenv 
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

load_dotenv()
DB_URL = os.getenv("DB_URL")

engine = create_async_engine(DB_URL, echo=True)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)