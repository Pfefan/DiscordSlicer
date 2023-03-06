import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.saved_files import Base, SavedFile


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_000_add(session):
    saved_file = SavedFile(
        user_id=1,
        channel_id=2,
        file_name='test.txt',
        file_size='1024',
        file_type='txt'
    )
    session.add(saved_file)
    session.commit()

    saved_file_query = session.query(SavedFile).filter_by(user_id=1).first()
    assert saved_file_query.user_id == saved_file.user_id
    assert saved_file_query.channel_id == saved_file.channel_id
    assert saved_file_query.file_name == saved_file.file_name
    assert saved_file_query.file_size == saved_file.file_size
    assert saved_file_query.file_type == saved_file.file_type


def test_001_query(session):
    saved_file_1 = SavedFile(
        user_id=1,
        channel_id=2,
        file_name='test1.txt',
        file_size='1024',
        file_type='txt'
    )
    saved_file_2 = SavedFile(
        user_id=1,
        channel_id=2,
        file_name='test2.txt',
        file_size='2048',
        file_type='txt'
    )
    session.add_all([saved_file_1, saved_file_2])
    session.commit()

    saved_files_query = session.query(SavedFile).filter_by(user_id=1).all()
    assert len(saved_files_query) == 2
    assert saved_files_query[0].user_id == saved_file_1.user_id
    assert saved_files_query[0].channel_id == saved_file_1.channel_id
    assert saved_files_query[0].file_name == saved_file_1.file_name
    assert saved_files_query[0].file_size == saved_file_1.file_size
    assert saved_files_query[0].file_type == saved_file_1.file_type
    assert saved_files_query[1].user_id == saved_file_2.user_id
    assert saved_files_query[1].channel_id == saved_file_2.channel_id
    assert saved_files_query[1].file_name == saved_file_2.file_name
    assert saved_files_query[1].file_size == saved_file_2.file_size
    assert saved_files_query[1].file_type == saved_file_2.file_type


def test_002_delete(session):
    saved_file = SavedFile(
        user_id=1,
        channel_id=2,
        file_name='test.txt',
        file_size='1024',
        file_type='txt'
    )
    session.add(saved_file)
    session.commit()

    session.delete(saved_file)
    session.commit()

    saved_file_query = session.query(SavedFile).filter_by(user_id=1).first()
    assert saved_file_query is None


def test_003_update(session):
    saved_file = SavedFile(
        user_id=1,
        channel_id=2,
        file_name='test.txt',
        file_size='1024',
        file_type='txt'
    )
    session.add(saved_file)
    session.commit()

    saved_file.file_name = 'new.txt'
    session.add(saved_file)
    session.commit()

    saved_file_query = session.query(SavedFile).filter_by(user_id=1).first()
    assert saved_file_query.file_name == saved_file.file_name
