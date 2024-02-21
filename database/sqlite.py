from utils.envvars import get_db_url
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


SQLITE_DB_URL = get_db_url()
engine = create_engine(SQLITE_DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SqliteDB:
    def __init__(self) -> None:
        self._engine = engine
        self._session_factory = SessionLocal
        self._base = Base

    def get_session(self):
        return self._session_factory()
    
    def get_engine(self):
        return self._engine

    def get_db(self):
        db = self.get_session()
        try:
            yield db
        finally:
            db.close()