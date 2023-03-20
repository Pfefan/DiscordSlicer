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
    file = [69, 420, "myfile", "16Gb", "exe"]

    session.insert_file(*file)
    files = session.get_files()

    assert len(files) == 1
    assert files[0].file_id == 1
    assert files[0].user_id == file[0]
    assert files[0].channel_id == file[1]
    assert files[0].file_name == file[2]
    assert files[0].file_size == file[3]
    assert files[0].file_type == file[4]

def test_get_files(session):
    """
    Tests that the `delete_by_channel_id` method deletes all files associated with a given channel.

    Args:
        session (LocalDBManager): The LocalDBManager instance configured for testing.
    """
    in_files = [(69, 420, "myfile", "16Gb", "exe"), (34, 187, "file", "10MB", "pdf")]

    for file in in_files:
        session.insert_file(*file)

    files = session.get_files()
    assert len(files) == 2
    assert (files[0].user_id, files[0].channel_id, files[0].file_name, files[0].file_size,
            files[0].file_type) == in_files[0]
    assert (files[1].user_id, files[1].channel_id, files[1].file_name, files[1].file_size,
            files[1].file_type) == in_files[1]
    assert files[0].file_id == 1
    assert files[1].file_id == 2

def test_delete_by_channel_id(session):
    """
    Tests that the `find_by_id` method returns the channel ID associated with a given file ID.

    Args:
        session (LocalDBManager): The LocalDBManager instance configured for testing.
    """
    in_files = [(69, 420, "myfile", "16Gb", "exe"), (34, 187, "file", "10MB", "pdf")]

    for file in in_files:
        session.insert_file(*file)

    session.delete_by_channel_id(420)
    session.delete_by_channel_id(187)

    files = session.get_files()
    assert len(files) == 0

def test_find_by_id(session):
    """
    Test the find_by_id method of the LocalDBManager class.

    This method tests whether the find_by_id method of the LocalDBManager class correctly
    retrieves the channel ID associated with a file given its ID.

    Args:
        session (pytest.fixture): A fixture that sets up a testing database session.

    Returns:
        None

    """
    session.insert_file(69, 420, "file1", 100, "txt")
    file_id = session.get_files()[0].id
    channel_id = session.find_by_id(file_id)
    assert channel_id == 420

def test_find_by_filename(session):
    """
    Test the find_by_filename method of the LocalDBManager class.

    This method tests whether the find_by_filename method of the LocalDBManager class correctly
    retrieves the channel ID associated with a file given its name.

    Args:
        session (pytest.fixture): A fixture that sets up a testing database session.

    Returns:
        None

    """
    session.insert_file(69, 420, "file1", 100, "txt")
    channel_id = session.find_by_filename("file1")
    assert channel_id == 420

def test_find_by_channel_id(session):
    """
    Test the find_by_channel_id method of the LocalDBManager class.

    This method tests whether the find_by_channel_id method of the LocalDBManager class correctly
    retrieves the channel ID associated with a file given the channel ID.

    Args:
        session (pytest.fixture): A fixture that sets up a testing database session.

    Returns:
        None

    """
    session.insert_file(69, 420, "file1", 100, "txt")
    file_id = session.get_files()[0].channel_id
    channel_id = session.find_by_channel_id(file_id)
    assert channel_id == 420

def test_find_name_by_channel_id(session):
    """
    Test the find_name_by_channel_id method of the LocalDBManager class.

    This method tests whether the find_name_by_channel_id method of the LocalDBManager class
    correctly retrieves the name of a file given the channel ID.

    Args:
        session (pytest.fixture): A fixture that sets up a testing database session.

    Returns:
        None

    """
    session.insert_file(69, 420, "file1", 100, "txt")
    file_name = session.find_name_by_channel_id(420)
    assert file_name == "file1"

def test_find_fullname_by_channel_id(session):
    """
    Test the find_fullname_by_channel_id method of the LocalDBManager class.

    This method tests whether the find_fullname_by_channel_id method of the LocalDBManager class
    correctly retrieves the full name of a file (including extension) given the channel ID.

    Args:
        session (pytest.fixture): A fixture that sets up a testing database session.

    Returns:
        None

    """
    session.insert_file(69, 420, "file1", 100, "txt")
    full_name = session.find_fullname_by_channel_id(420)
    assert full_name == "file1.txt"
