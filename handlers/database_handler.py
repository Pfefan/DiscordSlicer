from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from db.saved_files import Base, SavedFile
from logging_formatter import ConfigLogger


class FileManager:
    def __init__(self):
        """
        Initialize the database manager.
        """
        self.session_maker = None
        
        self.logger = ConfigLogger().setup()
    
    def configure_database(self):
        """configure database for normal programm execution"""
        engine = create_engine("sqlite:///db/database.db")
        Base.metadata.create_all(engine)
        self.session_maker = sessionmaker(bind=engine)


    def configure_database_test(self):
        """configures database for test execution"""
        engine = sqlalchemy.create_engine('sqlite:///:memory:')

        Base.metadata.create_all(engine)
        self.session_maker = sqlalchemy.orm.sessionmaker()
        self.session_maker.configure(bind=engine)

    def add_file(self, userid, channel_id, file_name, file_size, file_type):
        session = self.session_maker()
        file = SavedFile(user_id=userid, channel_id=channel_id, file_name=file_name, file_size=file_size, file_type=file_type)
        session.add(file)
        session.commit()
        session.close()
        self.logger.info("Saved data to database")

    def get_files(self):
        session = self.session_maker()
        files = session.query(SavedFile).all()
        session.close()
        self.logger.info("Got file data from database")
        return files

    def find_by_id(self, file_id):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(id=file_id).first()
        session.close()
        return file.channel_id if file else None

    def find_by_filename(self, filename):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(file_name=filename).first()
        session.close()
        return file.channel_id if file else None

    def find_by_channel_name(self, channel_id):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        session.close()
        return file.channel_id if file else None

    def find_name_by_channel_id(self, channel_id):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        session.close()
        return file.file_name if file else "No file found"