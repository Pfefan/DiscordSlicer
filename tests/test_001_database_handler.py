import pytest
from handlers.database_handler import Local_DB_Manager


@pytest.fixture
def session():
    db_manager = Local_DB_Manager()
    db_manager.configure_database_test()
    yield db_manager
    db_manager.session_maker().close()

def test_insert_file(session):
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
    in_files = [(69, 420, "myfile", "16Gb", "exe"), (34, 187, "file", "10MB", "pdf")]

    for file in in_files:
        session.insert_file(*file)

    files = session.get_files()
    assert len(files) == 2
    assert (files[0].user_id, files[0].channel_id, files[0].file_name, files[0].file_size, files[0].file_type) == in_files[0]
    assert (files[1].user_id, files[1].channel_id, files[1].file_name, files[1].file_size, files[1].file_type) == in_files[1]


def test_find_by_id(session):
    session.insert_file(69, 420, "file1", 100, "txt")
    file_id = session.get_files()[0].id
    channel_id = session.find_by_id(file_id)
    assert channel_id == 420

def test_find_by_filename(session):
    session.insert_file(69, 420, "file1", 100, "txt")
    channel_id = session.find_by_filename("file1")
    assert channel_id == 420

def test_find_by_channel_id(session):
    session.insert_file(69, 420, "file1", 100, "txt")
    file_id = session.get_files()[0].id
    channel_id = session.find_by_channel_id(420)
    assert channel_id == 420

def test_find_name_by_channel_id(session):
    session.insert_file(69, 420, "file1", 100, "txt")
    file_name = session.find_name_by_channel_id(420)
    assert file_name == "file1"

def test_find_fullname_by_channel_id(session):
    session.insert_file(69, 420, "file1", 100, "txt")
    full_name = session.find_fullname_by_channel_id(420)
    assert full_name == "file1.txt"

