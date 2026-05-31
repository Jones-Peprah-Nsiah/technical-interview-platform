from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import QuestionCreate, QuestionResponse, QuestionUpdate
from crud import (
    get_room_by_id,
    create_question,
    get_questions_by_room,
    get_question_by_id,
    delete_question,
    update_question,
    get_question_by_title_and_room
)
from auth import get_current_user_from_token


router = APIRouter(tags=["Questions"])


@router.get(
    "/rooms/{room_id}/questions",
    response_model=list[QuestionResponse]
)
def get_room_questions(
    room_id: int,
    db: Session = Depends(get_db)
):
    room = get_room_by_id(db, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    return get_questions_by_room(db, room_id)


@router.post(
    "/rooms/{room_id}/questions",
    response_model=QuestionResponse
)
def add_question_to_room(
    room_id: int,
    question: QuestionCreate,
    token: str,
    db: Session = Depends(get_db)
):
    allowed_difficulties = ["easy", "medium", "hard"]

    if question.difficulty not in allowed_difficulties:
        raise HTTPException(
            status_code=400,
            detail="Invalid difficulty. Use easy, medium, or hard"
        )

    current_user = get_current_user_from_token(token, db)

    if current_user.role != "interviewer":
        raise HTTPException(
            status_code=403,
            detail="Only interviewers can add questions"
        )

    room = get_room_by_id(db, room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to add questions to this room"
        )
    
    existing_question = get_question_by_title_and_room(
    db,
    room_id,
    question.title
)

    if existing_question:
        raise HTTPException(
        status_code=400,
        detail="Question already exists in this room"
    )

    return create_question(db, room_id, question)


@router.get("/questions/{question_id}", response_model=QuestionResponse)
def get_single_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    question = get_question_by_id(db, question_id)

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return question


@router.delete("/questions/{question_id}")
def delete_interview_question(
    question_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_token(token, db)

    if current_user.role != "interviewer":
        raise HTTPException(
            status_code=403,
            detail="Only interviewers can delete questions"
        )

    question = get_question_by_id(db, question_id)

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    room = get_room_by_id(db, question.room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to delete this question"
        )

    delete_question(db, question_id)

    return {
        "message": "Question deleted successfully"
    }

@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_interview_question(
    question_id: int,
    question_data: QuestionUpdate,
    token: str,
    db: Session = Depends(get_db)
):
    allowed_difficulties = ["easy", "medium", "hard"]

    if question_data.difficulty not in allowed_difficulties:
        raise HTTPException(
            status_code=400,
            detail="Invalid difficulty. Use easy, medium, or hard"
        )

    current_user = get_current_user_from_token(token, db)

    if current_user.role != "interviewer":
        raise HTTPException(
            status_code=403,
            detail="Only interviewers can update questions"
        )

    question = get_question_by_id(db, question_id)

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    room = get_room_by_id(db, question.room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if room.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to update this question"
        )

    return update_question(db, question_id, question_data)