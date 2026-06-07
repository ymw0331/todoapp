from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:mypassword@localhost:5432/todoapp"


# allow one thread to access the database at a time, prevent accidental data connection issues
engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# db object is used to interact with the database, and is created for each request
Base = declarative_base()
