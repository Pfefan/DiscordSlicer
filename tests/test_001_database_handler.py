import pytest
from handlers.database_handler import Local_DB_Manager
from local_db.saved_files import Base, SavedFile

@pytest.fixture
def session():
    db_manager = Local_DB_Manager()
    db_manager.configure_database_test()
    yield db_manager
    db_manager.session_maker().close()

def test_insert_file(session):
    file = [69, 420, "myfile", "16Gb", "exe"]
    session.insert_file(*file)

    saved_file_query = session.session_maker().query(SavedFile).filter_by(user_id=69).first()
    assert saved_file_query.user_id == file[0]
    assert saved_file_query.channel_id == file[1]
    assert saved_file_query.file_name == file[2]
    assert saved_file_query.file_size == file[3]
    assert saved_file_query.file_type == file[4]

def test_get_files(session):
    initial_num_files = len(session.get_files())
    file1 = [1, 1, "file1", "1KB", "txt"]
    session.insert_file(*file1)
    file2 = [2, 2, "file2", "2KB", "txt"]
    session.insert_file(*file2)
    assert len(session.get_files()) == initial_num_files + 2

def test_find_by_id(session):
    file = [69, 420, "myfile", "16Gb", "exe"]
    session.insert_file(*file)

    saved_file_id = session.session_maker().query(SavedFile).filter_by(user_id=69).first().id
    assert session.find_by_id(saved_file_id) == file[1]

def test_find_by_filename(session):
    file = [69, 420, "myfile", "16Gb", "exe"]
    session.insert_file(*file)

    assert session.find_by_filename("myfile") == file[1]

def test_find_by_channel_name(session):
    file = [69, 420, "myfile", "16Gb", "exe"]
    session.insert_file(*file)

    assert session.find_by_channel_name(420) == file[1]

def test_find_name_by_channel_id(session):
    file = [69, 420, "myfile", "16Gb", "exe"]
    session.insert_file(*file)

    assert session.find_name_by_channel_id(420) == file[2]
