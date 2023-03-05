from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.saved_files import Base, SavedFile
from logging_formatter import ConfigLogger


class FileManager:
    def __init__(self):
        self.engine = create_engine("sqlite:///db/database.db")
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.logger = ConfigLogger().setup()

    def add_file(self, userid, channel_id, file_name, file_size, file_type):
        session = self.Session()
        file = SavedFile(user_id=userid, channel_id=channel_id, file_name=file_name, file_size=file_size, file_type=file_type)
        session.add(file)
        session.commit()
        session.close()
        self.logger.info("Saved data to database")

    def get_files(self):
        session = self.Session()
        files = session.query(SavedFile).all()
        session.close()
        self.logger.info("Got file data from database")
        return files