# pylint: disable=redefined-outer-name
"""
This module contains test cases for database model.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from local_db.saved_files import Base, SavedFile


@pytest.fixture(scope="module")
def test_db():
    """
    Create an in-memory SQLite database and a session to interact with it.
    """
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_saved_file(test_db):
    """
    Test the creation of a saved file in the database.
    """
    file = SavedFile(user_id=1, channel_id=1, file_name="file1", file_size="100MB", file_type="txt", num_files="4")
    test_db.add(file)
    test_db.commit()
    assert file.id is not None


def test_retrieve_saved_file(test_db):
    """
    Test the retrieval of a saved file from the database.
    """
    file = SavedFile(user_id=1, channel_id=1, file_name="file1", file_size="100MB", file_type="txt", num_files="4")
    test_db.add(file)
    test_db.commit()

    retrieved_file = test_db.query(SavedFile).filter_by(id=file.id).first()
    assert retrieved_file.id == file.id
    assert retrieved_file.user_id == file.user_id
    assert retrieved_file.channel_id == file.channel_id
    assert retrieved_file.file_name == file.file_name
    assert retrieved_file.file_size == file.file_size
    assert retrieved_file.file_type == file.file_type
    assert retrieved_file.num_files == file.num_files


def test_update_saved_file(test_db):
    """
    Test the update of a saved file in the database.
    """
    file = SavedFile(user_id=1, channel_id=1, file_name="file1", file_size="100MB", file_type="txt", num_files="4")
    test_db.add(file)
    test_db.commit()

    file.file_name = "new_file_name"
    test_db.commit()

    retrieved_file = test_db.query(SavedFile).filter_by(id=file.id).first()
    assert retrieved_file.file_name == "new_file_name"


def test_delete_saved_file(test_db):
    """
    Test the deletion of a saved file from the database.
    """
    file = SavedFile(user_id=1, channel_id=1, file_name="file1", file_size="100MB", file_type="txt", num_files="4")
    test_db.add(file)
    test_db.commit()

    test_db.delete(file)
    test_db.commit()

    assert test_db.query(SavedFile).filter_by(id=file.id).first() is None
