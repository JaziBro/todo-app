# databse.py
from contextlib import asynccontextmanager
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine
from fastapi_todo.settings import DATABASE_URL
import os
from fastapi_todo.models import models
from sqlmodel import select

def get_session():
    with Session(engine) as session: 
        yield session

_ = load_dotenv(find_dotenv())

connection_string = str(os.environ["DATABASE_URL"]).replace("postgresql","postgresql+psycopg")

if DATABASE_URL is None:
    raise RuntimeError("Database environment variable is not set")

engine = create_engine(connection_string, connect_args={"sslmode": "require"}, pool_recycle=300,)
   
def create_db_and_tables():
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    try:
        yield
    finally:
        print("Dropping tables...")
        print("Tables dropped.")
