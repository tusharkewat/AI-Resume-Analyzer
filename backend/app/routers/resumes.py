import asyncio
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, ResumeListItem
from app.dependencies import get_current_user
from app.utils.file_validation import validate_uploaded_file, sanitize_filename
from app.services.resume_parser import ResumeParserService
from app.services.information_extractor import InformationExtractorService
from app.utils.exceptions import InvalidFileError
from app.utils.rate_limiter import rate_limit
from app.config import settings

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(settings.RATE_LIMIT_UPLOAD_PER_MINUTE, 60, "resume_upload"))]
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Validate file size, extension, magic bytes
        file_bytes = await validate_uploaded_file(file)
    except InvalidFileError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    clean_filename = sanitize_filename(file.filename)
    ext = os.path.splitext(clean_filename)[1].lower()

    # Offload parsing and NLP extraction to threadpool to keep event loop responsive
    try:
        extracted_text, metadata = await asyncio.to_thread(
            ResumeParserService.extract_text, file_bytes, ext
        )
        structured_data = await asyncio.to_thread(
            InformationExtractorService.extract_structured_data, extracted_text
        )
    except InvalidFileError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unable to process resume: {str(e)}"
        )

    # Persist Resume entity
    resume = Resume(
        user_id=current_user.id,
        original_filename=clean_filename,
        file_type=ext.replace(".", ""),
        extracted_text=extracted_text,
        structured_data=structured_data.model_dump()
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeResponse.model_validate(resume)


@router.get("", response_model=List[ResumeListItem])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    return [ResumeListItem.model_validate(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return ResumeResponse.model_validate(resume)


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(resume)
    db.commit()
    return {"message": "Resume and related analyses deleted successfully."}
