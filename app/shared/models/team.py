from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.shared.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    creator_id = Column(Integer, ForeignKey('users.id'))

class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(String, default="member")