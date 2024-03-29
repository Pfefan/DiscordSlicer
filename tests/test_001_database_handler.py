# pylint: disable=redefined-outer-name
"""
This module contains test functions for the LocalDBManager class,
which is used to interact with a local database.
"""
import pytest
from handlers.database_handler import LocalDBManager

@pytest.fixture
def session():
    """
    Fixture that creates and configures a LocalDBManager for testing.

    Yields:
        LocalDBManager: The configured LocalDBManager instance.
    """
    db_manager = LocalDBManager()
    db_manager.configure_database_test()
    yield db_manager
    db_manager.session_maker().close()

def test_insert_file(session):
    """
    Tests that a file can be inserted into the database using the `insert_file` method.

    Args:
        session (LocalDBManager): The LocalDBManager instance configured for testing.
    """
    file = [69, 420, "myfile", "16Gb", "exe", 6]

    session.insert_file(*file)
    files = session.get_files()

    assert len(files) == 1
    assert files[0].file_id == 1
    assert files[0].user_id == file[0]
    assert files[0].channel_id == file[1]
    assert files[0].file_name == file[2]
    assert files[0].file_size == file[3]
    assert files[0].file_type == file[4]
    assert files[0].num_files == file[5]

def test_get_files(session):
    """
    Tests that the `delete_by_channel_id` method deletes all files associated with a given channel.

    Args:
        session (LocalDBManager): The LocalDBManager instance configured for testing.
    """
    in_files = [(69, 420, "myfile", "16Gb", "exe", 10), (34, 187, "file", "10MB", "pdf", 1)]

    for file in in_files:
        session.insert_file(*file)

    files = session.get_files()
    assert len(files) == 2
    assert (files[0].user_id, files[0].channel_id, files[0].file_name, files[0].file_size,
            files[0].file_type, files[0].num_files) == in_files[0]
    assert (files[1].user_id, files[1].channel_id, files[1].file_name, files[1].file_size,
            files[1].file_type, files[1].num_files) == in_files[1]
    assert files[0].file_id == 1
    assert files[1].file_id == 2

def test_delete_by_channel_id(session):
    """
    Tests that the `find_by_id` method returns the channel ID associated with a given file ID.

    Args:
        session (LocalDBManager): The LocalDBManager instance configured for testing.
    """
    in_files = [(69, 420, "myfile", "16Gb", "exe", 10), (34, 187, "file", "10MB", "pdf", 1)]

    for file in in_files:
        session.insert_file(*file)

    session.delete_by_channel_id(420)
    session.delete_by_channel_id(187)

    files = session.get_files()
    assert len(files) == 0

def test_get_channelid_by_id(session):
    """
    Test the get_channelid_by_id method of the LocalDBManager class.

    This method tests whether the get_channelid_by_id method of the LocalDBManager class correctly
    retrieves the channel ID associated with a file given its ID.

    Args:
        session (pytest.fixture): A fixture that sets up a testing database session.

    Returns:
        None

    """
    session.insert_file(69, 420, "file1", 100, "txt", 12)
    file_id = session.get_files()[0].id
    channel_id = session.get_channelid_by_id(file_id)
    assert channel_id == 420

def test_get_channelid_by_filename(session):
    """
    Test the get_channelid_by_filename method of the LocalDBManager class.

    This method tests whether the get_channelid_by_filename method of the LocalDBManager class correctly
    retrieves the channel ID associated with a file given its name.

    Args:
        session (pytest.fixture): A fixture that sets up a testing database session.

    Returns:
        None

    """
    session.insert_file(69, 420, "file1", 100, "txt", 69)
    channel_id = session.get_channelid_by_filename("file1")
    assert channel_id == 420

def test_get_channelid_by_channelid(session):
    """
    Test the get_channelid_by_channelid method of the LocalDBManager class.

    This method tests whether the get_channelid_by_channelid method of the LocalDBManager class correctly
    retrieves the channel ID associated with a file given the channel ID.

    Args:
        session (pytest.fixture): A fixture that sets up a testing database session.

    Returns:
        None

    """
    session.insert_file(69, 420, "file1", 100, "txt", 420)
    file_id = session.get_files()[0].channel_id
    channel_id = session.get_channelid_by_channelid(file_id)
    assert channel_id == 420
