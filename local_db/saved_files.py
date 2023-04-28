"""
Model structure declaration for local DB
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SavedFile(Base): # pylint: disable=too-few-public-methods
    """Saved Files table"""
    __tablename__ = "saved_files"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    channel_id = Column(Integer, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    num_files = Column(Integer, nullable=False)
