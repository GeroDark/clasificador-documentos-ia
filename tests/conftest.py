from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models.document import Document
from app.models.processing_job import ProcessingJob


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Document.__table__.create(bind=engine, checkfirst=True)
ProcessingJob.__table__.create(bind=engine, checkfirst=True)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_test_db() -> Generator[None, None, None]:
    with TestingSessionLocal() as db:
        db.execute(delete(ProcessingJob))
        db.execute(delete(Document))
        db.commit()

    yield

    with TestingSessionLocal() as db:
        db.execute(delete(ProcessingJob))
        db.execute(delete(Document))
        db.commit()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def document_factory(db_session: Session):
    def factory(**overrides) -> Document:
        document = Document(
            original_filename=overrides.get("original_filename", "contrato.pdf"),
            stored_filename=overrides.get("stored_filename", "stored-contrato.pdf"),
            file_path=overrides.get("file_path", "uploads/stored-contrato.pdf"),
            content_type=overrides.get("content_type", "application/pdf"),
            size_bytes=overrides.get("size_bytes", 1024),
            status=overrides.get("status", "queued"),
            created_at=overrides.get("created_at", datetime.now(timezone.utc)),
        )
        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)
        return document

    return factory


@pytest.fixture
def job_factory(db_session: Session, document_factory):
    def factory(**overrides) -> ProcessingJob:
        document_id = overrides.get("document_id")
        if document_id is None:
            document_id = document_factory().id

        job = ProcessingJob(
            document_id=document_id,
            task_id=overrides.get("task_id", "task-123"),
            status=overrides.get("status", "queued"),
            error_message=overrides.get("error_message"),
            created_at=overrides.get("created_at", datetime.now(timezone.utc)),
            started_at=overrides.get("started_at"),
            finished_at=overrides.get("finished_at"),
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        return job

    return factory
