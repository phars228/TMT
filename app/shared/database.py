from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.shared.config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from app.shared.models.user import User
    from app.shared.models.team import Team, TeamMember
    from app.shared.models.task import Task, TaskAssignment
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()