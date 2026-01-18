
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Generation(Base):
    __tablename__ = 'generations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False) # Foreign key logic handled manually or via simple ID for now
    filename = Column(String, nullable=False)
    image_filename = Column(String, nullable=True) # New column for saving visualization
    prompt = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Ensure data directory exists
# Assuming run from root, so music_gen/data is correct
if not os.path.exists("music_gen/data"):
    os.makedirs("music_gen/data", exist_ok=True)

# Connect to SQLite
engine = create_engine('sqlite:///music_gen/data/app.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
