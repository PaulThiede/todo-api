import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv
import os

load_dotenv()

# Engine: Verbindung zur DB
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

# Session: Verbindungskanal pro Anfrage
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Basis-Klasse für alle ORM-Modelle
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
