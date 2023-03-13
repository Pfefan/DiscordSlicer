import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from local_db.saved_files import Base, SavedFile


@pytest.fixture(scope="module")
def db():
    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_create_saved_file(db):
    file = SavedFile(user_id=1, channel_id=1, file_name="file1", file_size="100MB", file_type="txt")
    db.add(file)
    db.commit()
    assert file.id is not None


def test_retrieve_saved_file(db):
    file = SavedFile(user_id=1, channel_id=1, file_name="file1", file_size="100MB", file_type="txt")
    db.add(file)
    db.commit()

    retrieved_file = db.query(SavedFile).filter_by(id=file.id).first()
    assert retrieved_file.id == file.id
    assert retrieved_file.user_id == file.user_id
    assert retrieved_file.channel_id == file.channel_id
    assert retrieved_file.file_name == file.file_name
    assert retrieved_file.file_size == file.file_size
    assert retrieved_file.file_type == file.file_type


def test_update_saved_file(db):
    file = SavedFile(user_id=1, channel_id=1, file_name="file1", file_size="100MB", file_type="txt")
    db.add(file)
    db.commit()

    file.file_name = "new_file_name"
    db.commit()

    retrieved_file = db.query(SavedFile).filter_by(id=file.id).first()
    assert retrieved_file.file_name == "new_file_name"


def test_delete_saved_file(db):
    file = SavedFile(user_id=1, channel_id=1, file_name="file1", file_size="100MB", file_type="txt")
    db.add(file)
    db.commit()

    db.delete(file)
    db.commit()

    assert db.query(SavedFile).filter_by(id=file.id).first() is None

