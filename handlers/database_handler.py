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

    def find_by_id(self, file_id):
        session = self.Session()
        file = session.query(SavedFile).filter_by(id=file_id).first()
        session.close()
        return file.channel_id if file else None

    def find_by_filename(self, filename):
        session = self.Session()
        file = session.query(SavedFile).filter_by(file_name=filename).first()
        session.close()
        return file.channel_id if file else None

    def find_by_channel_name(self, channel_id):
        session = self.Session()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        session.close()
        return file.channel_id if file else None

    def find_name_by_channel_id(self, channel_id):
        session = self.Session()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        session.close()
        return file.file_name if file else "No file found"