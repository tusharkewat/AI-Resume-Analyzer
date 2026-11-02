import io
import pytest
from typing import Generator
from starlette.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import docx
import fitz

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.security.password import get_password_hash
from app.security.jwt import create_access_token
from app.utils.rate_limiter import limiter

# Test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture(scope="function")
def db_session() -> Generator:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_a(db_session) -> User:
    user = User(
        full_name="Alice Developer",
        email="alice@example.com",
        hashed_password=get_password_hash("StrongPassword123!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers_user_a(test_user_a) -> dict:
    token = create_access_token({"sub": str(test_user_a.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_user_b(db_session) -> User:
    user = User(
        full_name="Bob Engineer",
        email="bob@example.com",
        hashed_password=get_password_hash("SecurePassword456!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers_user_b(test_user_b) -> dict:
    token = create_access_token({"sub": str(test_user_b.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Generates a real PDF in memory with text."""
    doc = fitz.open()
    page = doc.new_page()
    text = (
        "Alice Developer\n"
        "alice@example.com | (555) 123-4567 | San Francisco, CA\n\n"
        "Summary\n"
        "Experienced Full Stack Software Engineer specializing in Python, FastAPI, React, and cloud architectures.\n\n"
        "Skills\n"
        "Python, FastAPI, Django, React, TypeScript, PostgreSQL, Docker, Kubernetes, AWS, Git, Problem Solving\n\n"
        "Experience\n"
        "Senior Software Engineer | Tech Corp | 2021 - Present\n"
        "- Engineered scalable microservices handling 50k requests per second using FastAPI and Docker.\n"
        "- Optimized PostgreSQL queries, reducing database load by 35%.\n"
        "- Spearheaded adoption of CI/CD pipelines with GitHub Actions.\n\n"
        "Software Engineer | Web Systems | 2018 - 2021\n"
        "- Built responsive React and TypeScript frontend applications.\n"
        "- Designed RESTful APIs in Python with PostgreSQL.\n\n"
        "Education\n"
        "Bachelor of Science in Computer Science | UC Berkeley | 2018\n"
    )
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


@pytest.fixture
def sample_docx_bytes() -> bytes:
    """Generates a real DOCX in memory with paragraphs and tables."""
    doc = docx.Document()
    doc.add_heading("Bob Engineer", 0)
    doc.add_paragraph("bob@example.com | (555) 987-6543 | New York, NY")
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph("Backend Developer with deep expertise in Python, Go, Kubernetes, and Distributed Systems.")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, Go, Docker, Kubernetes, AWS, PostgreSQL, Redis, Microservices, Leadership")
    doc.add_heading("Work Experience", level=1)
    doc.add_paragraph("Staff Backend Engineer | CloudScale Inc | 2020 - Present")
    doc.add_paragraph("- Led architectural modernization to containerized Kubernetes microservices.")
    doc.add_paragraph("- Designed distributed caching system using Redis, decreasing response times by 40%.")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("Master of Science in Software Engineering | NYU | 2020")
    
    # Table test
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Certification"
    table.cell(0, 1).text = "AWS Certified Solutions Architect"
    table.cell(1, 0).text = "Year"
    table.cell(1, 1).text = "2022"

    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
