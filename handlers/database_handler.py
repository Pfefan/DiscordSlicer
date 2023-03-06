import configparser

import pymongo
import sqlalchemy
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from local_db.saved_files import Base, SavedFile
from logging_formatter import ConfigLogger


class Local_DB_Manager:
    def __init__(self):
        """
        Initialize the database manager.
        """
        self.session_maker = None
        
        self.logger = ConfigLogger().setup()
    
    def configure_database(self):
        """configure database for normal programm execution"""
        engine = create_engine("sqlite:///local_db/database.db")
        Base.metadata.create_all(engine)
        self.session_maker = sessionmaker(bind=engine)


    def configure_database_test(self):
        """configures database for test execution"""
        engine = sqlalchemy.create_engine('sqlite:///:memory:')

        Base.metadata.create_all(engine)
        self.session_maker = sqlalchemy.orm.sessionmaker()
        self.session_maker.configure(bind=engine)

    def insert_file(self, userid, channel_id, file_name, file_size, file_type):
        session = self.session_maker()
        file = SavedFile(user_id=userid, channel_id=channel_id, file_name=file_name, file_size=file_size, file_type=file_type)
        session.add(file)
        session.commit()
        session.close()
        self.logger.info("Saved data to local database")

    def get_files(self):
        session = self.session_maker()
        files = session.query(SavedFile).all()
        session.close()
        self.logger.info("Got file data from local database")
        return files

    def find_by(self, **kwargs):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(**kwargs).first()
        session.close()
        return file.channel_id if file else None

    def find_by_id(self, file_id):
        return self.find_by(id=file_id)

    def find_by_filename(self, filename):
        return self.find_by(file_name=filename)

    def find_by_channel_name(self, channel_id):
        return self.find_by(channel_id=channel_id)

    def find_name_by_channel_id(self, channel_id):
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        session.close()
        return file.file_name if file else "No file found"


class Cloud_DB_Manager():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        cluster = MongoClient(config['DEFAULT']['connection_string'])
        self.db = cluster[config['DEFAULT']['cluster_name']]
        self.collection = self.db["file_list"]
        self.counters = self.db["counters"]
        
        self.logger = ConfigLogger().setup()


    def insert_file(self, user_id, channel_id, file_name, file_size, file_type):
        """
        Inserts a new file document into the collection with an auto-incrementing file_id.
        """
        sequence_document = self.counters.find_one_and_update(
            {"_id": "file_id"},
            {"$inc": {"sequence_value": 1}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        file_id = sequence_document["sequence_value"]
        self.collection.insert_one({
            "_id": file_id,
            "user_id": user_id,
            "channel_id": channel_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type
        })
        self.logger.info("Saved data to cloud database")

    def get_files(self):
        results = self.collection.find()
        self.logger.info("Got file data from cloud database")
        return results

    def find_by(self, **kwargs):
        result = self.collection.find_one(kwargs)
        return result["channel_id"] if result else None

    def find_by_id(self, file_id):
        return self.find_by(_id=int(file_id))

    def find_by_filename(self, filename):
        return self.find_by(file_name=filename)

    def find_by_channel_name(self, channel_id):
        return self.find_by(channel_id=int(channel_id))

    def find_name_by_channel_id(self, channel_id):
        result = self.collection.find_one({"channel_id": channel_id}, {"file_name": 1})
        return result.get("file_name", "No file found")