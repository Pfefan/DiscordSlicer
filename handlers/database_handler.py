# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
"""Provides a HybridDBhandler class for handling database data.

This class acts as a switch between a local SQLite database and a remote MongoDB
Atlas database depending on the value of 'use_cloud_database' in the 'config.ini' file.

Classes:
- HybridDBhandler: main class for handling file data.

"""
import configparser

import pymongo
import sqlalchemy
from pymongo import MongoClient
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from local_db.saved_files import Base, SavedFile
from logging_formatter import ConfigLogger


class HybridDBhandler:
    """
    A class for managing files in a hybrid database, which can either be a
    local or a cloud database.

    Attributes:
    - use_cloud_database (bool): A flag indicating whether to use the cloud database
    or the local database.
    - local_db (LocalDBManager): An instance of the local database manager.
    - cloud_db (CloudDBManager): An instance of the cloud database manager.

    Methods:
    - insert_file(userid, channel_id, file_name, file_size, file_type, num_files):
    Inserts a file into the database.
    - get_files(): Returns all the files from the database.
    - get_file_by_channelid(channel_id): Retrieves the data for a file associated with
    a given channel ID.
    - get_channelid_by_fileid(file_id): Gets channel_id value from the database by the file_id.
    - get_channelid_by_filename(filename): Gets channel_id value from the database by the filename.
    - get_channelid_by_channelid(channel_id): Gets channel_id value from the database
    by the channel_id.
    - delete_by_channel_id(channel_id): Deletes a file from the database by channel id.
    """
    def __init__(self):
        """
        Initializes HybridDBhandler class.
        """
        config = configparser.ConfigParser()
        config.read('config.ini')
        use_cloud_database_str = config['DATABASE'].get('use_cloud_database', 'false')
        self.use_cloud_database = use_cloud_database_str.lower() == 'true'
        # database Classes
        self.local_db = LocalDBManager()
        self.local_db.configure_database()

        self.cloud_db = CloudDBManager(config)

    def insert_file(self, userid:int, channel_id:int, file_name:str, file_size:str, file_type:str, num_files:str):
        """
        Inserts a file into the database.

        Parameters:
        ----------
        userid : int
            The user id associated with the file.
        channel_id : int
            The channel id associated with the file.
        file_name : str
            The name of the file.
        file_size : str
            The size of the file.
        file_type : str
            The type of the file.
        num_files : str
            The amount of chunk files stored
        """
        if self.use_cloud_database:
            self.cloud_db.insert_file(userid, channel_id, file_name, file_size, file_type, num_files)
            return
        self.local_db.insert_file(userid, channel_id, file_name, file_size, file_type, num_files)

    def get_files(self):
        """
        Returns all the files from the database.
        """
        if self.use_cloud_database:
            files = self.cloud_db.get_files()
            files = [FileData(
                f['_id'], f['user_id'], f['channel_id'], f['file_id'],
                f['file_name'], f['file_size'], f['file_type'], f['num_files']
            ) for f in files]
            return files
        files = self.local_db.get_files()
        files = [FileData(
            f.id, f.user_id, f.channel_id, f.file_id,
            f.file_name, f.file_size, f.file_type, f.num_files
            ) for f in files]
        return files

    def get_file_by_channelid(self, channel_id):
        """
        Retrieves the data for a file associated with a given channel ID.

        Parameters:
        - channel_id (str): The ID of the channel to find the file for.

        Returns:
        - dict: A dictionary containing the data for the file, including
        its ID, name, size, and other
        relevant information.
        """
        if self.use_cloud_database:
            return self.cloud_db.get_file_by_channelid(channel_id)
        return self.local_db.get_file_by_channelid(channel_id)

    def get_channelid_by_fileid(self, file_id: str):
        """
        Gets channel_id value from the database by the file_id

        Parameters:
        ----------
        file_id : int
            The id of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        if self.use_cloud_database:
            return self.cloud_db.get_channelid_by_id(file_id)
        return self.local_db.get_channelid_by_id(file_id)

    def get_channelid_by_filename(self, filename:str):
        """
        Gets channel_id value from the database by the filename

        Parameters:
        ----------
        filename : str
            The filename of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        if self.use_cloud_database:
            return self.cloud_db.get_channelid_by_filename(filename)
        return self.local_db.get_channelid_by_filename(filename)

    def get_channelid_by_channelid(self, channel_id:int):
        """
        Gets channel_id value from the database by the channel_id

        Parameters:
        ----------
        channel_id : int
            The channel_id of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        if self.use_cloud_database:
            return self.cloud_db.get_channelid_by_channelid(channel_id)
        return self.local_db.get_channelid_by_channelid(channel_id)

    def delete_by_channel_id(self, channel_id):
        """
        Deletes a file from the database by channel id.

        Parameters:
        ----------
        channel_id : int
            The channel id associated with the file.
        """
        if self.use_cloud_database:
            return self.cloud_db.delete_by_channel_id(channel_id)
        return self.local_db.delete_by_channel_id(channel_id)

class FileData:
    """A class representing file data.

    Attributes:
        file_id (str): The file ID.
        user_id (str): The user ID who uploaded the file.
        channel_id (int): The channel ID where the file was uploaded.
        server_file_id (str): The file ID assigned by the server.
        file_name (str): The file name.
        file_size (int): The file size in bytes.
        file_type (str): The file type, e.g. 'pdf', 'jpg', etc.
        num_files (int): Nummer of files stored in discord channel
    """

    def __init__(self, file_pk, user_id, channel_id, file_id, file_name,
                 file_size, file_type, num_files):
        self.pk_file = file_pk
        self.user_id = user_id
        self.channel_id = channel_id
        self.file_id = file_id
        self.file_name = file_name
        self.file_size = file_size
        self.file_type = file_type
        self.num_files = num_files

class LocalDBManager:
    """
    A class for managing the local SQLite database.
    """

    def __init__(self):
        """
        Initialize the database manager.
        """
        self.session_maker = None
        self.logger = ConfigLogger().setup()

    def configure_database(self):
        """
        Configures the database for normal program execution.
        """
        engine = create_engine("sqlite:///local_db/database.db")
        Base.metadata.create_all(engine)
        self.session_maker = sessionmaker(bind=engine)

    def configure_database_test(self):
        """
        Configures the database for test execution.
        """
        engine = sqlalchemy.create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        self.session_maker = sqlalchemy.orm.sessionmaker()
        self.session_maker.configure(bind=engine)

    def insert_file(self, user_id, channel_id, file_name, file_size, file_type, num_files):
        """
        Inserts a file record into the database.

        Args:
            user_id (int): The user ID associated with the file.
            channel_id (int): The channel ID associated with the file.
            file_name (str): The name of the file.
            file_size (int): The size of the file in bytes.
            file_type (str): The file type (e.g., 'pdf', 'docx', 'jpg').
            num_files (int): amount of files uploaded to discord.

        Returns:
            None.
        """
        session = self.session_maker()
        max_file_id = session.query(func.max(SavedFile.file_id)).scalar() or 0  # pylint: disable=not-callable
        file_id = max_file_id + 1
        file = SavedFile(
            file_id=file_id,
            user_id=user_id,
            channel_id=channel_id,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            num_files=num_files
        )
        session.add(file)
        session.commit()
        session.close()
        self.logger.info("Saved data to local database")

    def get_files(self):
        """
        Retrieves all file records from the database.

        Returns:
            A list of `SavedFile` objects representing the file records.
        """
        session = self.session_maker()
        files = session.query(SavedFile).all()
        session.close()
        self.logger.info("Got file data from local database")
        return files

    def get_file_by_channelid(self, channel_id):
        """
        Retrieves the data for a file associated with a given channel ID.

        Parameters:
        - channel_id (str): The ID of the channel to find the file for.

        Returns:
        - dict: A dictionary containing the data for the file, including
        its ID, name, size, and other
        relevant information.
        """
        session = self.session_maker()

        # query database for file with matching channel_id
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()

        if file is None:
            self.logger.info("No file data found for channel_id: %s", channel_id)
        else:
            self.logger.info("Got file data for channel_id: %s", channel_id)

        session.close()
        return file

    def find_by(self, **kwargs):
        """
        Finds a file record in the database based on the given criteria.

        Args:
            **kwargs: A dictionary containing the search criteria.

        Returns:
            The channel ID associated with the file if found, None otherwise.
        """
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(**kwargs).first()
        session.close()
        return file.channel_id if file else None

    def get_channelid_by_id(self, file_id):
        """
        Gets channel_id value from the database by the file_id

        Parameters:
        ----------
        file_id : int
            The id of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        return self.find_by(file_id=file_id)

    def get_channelid_by_filename(self, filename):
        """
        Gets channel_id value from the database by the filename

        Parameters:
        ----------
        filename : str
            The filename of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        return self.find_by(file_name=filename)

    def get_channelid_by_channelid(self, channel_id):
        """
        Gets channel_id value from the database by the channel_id

        Parameters:
        ----------
        channel_id : int
            The channel_id of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        return self.find_by(channel_id=channel_id)

    def delete_by_channel_id(self, channel_id):
        """
        Deletes a file record from the database based on its channel ID.

        Args:
            channel_id (int): The channel ID associated with the file.

        Returns:
            True if a file record was deleted, False otherwise.
        """
        session = self.session_maker()
        file = session.query(SavedFile).filter_by(channel_id=channel_id).first()
        if file is not None:
            session.delete(file)
            self.logger.info("Deleted file with channel_id=%s", channel_id)
            session.commit()
            session.close()
            return True
        self.logger.info("No file with channel_id=%s found", channel_id)
        session.close()
        return False


class CloudDBManager():
    """
    A class that manages the interaction with a cloud database for storing file information.
    """
    def __init__(self, config):
        """
        Initializes the CloudDBManager object with a configuration dictionary.
        """
        self.config = config

        cluster = MongoClient(config['DATABASE']['connection_string'])
        self.database = cluster[config['DATABASE']['cluster_name']]
        self.collection = self.database["file_list"]
        self.counters = self.database["counters"]

        self.logger = ConfigLogger().setup()

    def insert_file(self, user_id, channel_id, file_name, file_size, file_type, num_files):
        """
        Inserts a new file document into the collection with an auto-incrementing file_id.

        Args:
            user_id (str): The ID of the user who uploaded the file.
            channel_id (str): The ID of the channel where the file was uploaded.
            file_name (str): The name of the file.
            file_size (int): The size of the file in bytes.
            file_type (str): The type of the file.
            num_files (int): The amount of chunk files stored

        Returns:
            None
        """
        sequence_document = self.counters.find_one_and_update(
            {"_id": "file_id"},
            {"$inc": {"sequence_value": 1}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        file_id = sequence_document["sequence_value"]
        self.collection.insert_one({
            "user_id": user_id,
            "channel_id": channel_id,
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
            "num_files": num_files
        })
        self.logger.info("Saved data to cloud database")

    def get_files(self):
        """
        Retrieves all file documents from the collection.

        Parameters:
        - None.

        Returns:
        - A cursor object containing all file documents in the collection.
        """
        results = self.collection.find()
        self.logger.info("Got files from cloud database")
        return results

    def get_file_by_channelid(self, channel_id:str):
        """
        Retrieves the data for a file associated with a given channel ID.

        Parameters:
        - channel_id (str): The ID of the channel to find the file for.

        Returns:
        - dict: A dictionary containing the data for the file, including
        its ID, name, size, and other
        relevant information.
        """
        file = self.collection.find_one({"channel_id": channel_id})
        if file:
            self.logger.info("Got file data for the channel_id: %s", channel_id)
            return file
        else:
            self.logger.info("No file found for the channel_id: %s", channel_id)
            return None

    def find_by(self, **kwargs):
        """
        Retrieves a file document from the collection that matches the given query parameters.

        Parameters:
        - **kwargs: Keyword arguments representing the query parameters to match.

        Returns:
        - The channel_id of the matching file document if one is found, None otherwise.
        """
        result = self.collection.find_one(kwargs)
        return result["channel_id"] if result else None

    def get_channelid_by_id(self, file_id):
        """
        Gets channel_id value from the database by the file_id

        Parameters:
        ----------
        file_id : int
            The id of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        return self.find_by(file_id=int(file_id))

    def get_channelid_by_filename(self, filename):
        """
        Gets channel_id value from the database by the filename

        Parameters:
        ----------
        filename : str
            The filename of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        return self.find_by(file_name=filename)

    def get_channelid_by_channelid(self, channel_id):
        """
        Gets channel_id value from the database by the channel_id

        Parameters:
        ----------
        channel_id : int
            The channel_id of the file to be searched.

        Returns:
        -------
        channel_id or None:
            Returns the channel_id value or None if no file is found
        """
        return self.find_by(channel_id=int(channel_id))

    def delete_by_channel_id(self, channel_id):
        """
        Deletes a file document from the collection by its channel_id.

        Parameters:
        - channel_id: A string representing the ID of the channel where the file was uploaded.

        Returns:
        - True if a file document was found and deleted, False otherwise.
        """
        result = self.collection.delete_one({"channel_id": channel_id})
        if result.deleted_count == 1:
            self.logger.info("Deleted file with channel_id=%s", channel_id)
            return True
        self.logger.info("No file with channel_id=%s found", channel_id)
        return False
