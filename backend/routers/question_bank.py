from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import QuestionCreate, QuestionBankResponse
from crud import get_question_bank, get_bank_question_by_title, create_bank_question
from auth import get_current_user


router = APIRouter(tags=["Question Bank"])


@router.get("/question-bank", response_model=list[QuestionBankResponse])
def list_bank_questions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_question_bank(db)


@router.post("/question-bank", response_model=QuestionBankResponse)
def add_bank_question(
    question: QuestionCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_difficulties = ["easy", "medium", "hard"]

    if question.difficulty not in allowed_difficulties:
        raise HTTPException(
            status_code=400,
            detail="Invalid difficulty. Use easy, medium, or hard"
        )

    if current_user.role != "interviewer":
        raise HTTPException(
            status_code=403,
            detail="Only interviewers can add to the question bank"
        )

    existing = get_bank_question_by_title(db, question.title)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This question already exists in the bank"
        )

    return create_bank_question(db, question)
