from sqlalchemy.orm import Session

from models import User, Room, Participant, Question, QuestionBankItem, CodeSession
from schemas import UserCreate
from auth import hash_password


def create_user(db: Session, user: UserCreate, role: str = "candidate"):
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def create_room(db: Session, room, user_id: int):
    new_room = Room(
        title=room.title,
        description=room.description,
        user_id=user_id
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return new_room


def get_rooms(db: Session):
    return db.query(Room).all()


def get_room_by_id(db: Session, room_id: int):
    return db.query(Room).filter(Room.id == room_id).first()


def delete_room(db: Session, room_id: int):
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        return None

    db.delete(room)
    db.commit()

    return room


def join_room(db: Session, participant):
    new_participant = Participant(
        user_id=participant.user_id,
        room_id=participant.room_id,
        role=participant.role
    )

    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)

    return new_participant

def get_participant(db: Session, user_id: int, room_id: int):
    return (
        db.query(Participant)
        .filter(
            Participant.user_id == user_id,
            Participant.room_id == room_id
        )
        .first()
    )


def get_room_participants(db: Session, room_id: int):
    return (
        db.query(Participant)
        .filter(Participant.room_id == room_id)
        .all()
    )


def update_room(db: Session, room_id: int, room_data):
    room = db.query(Room).filter(Room.id == room_id).first()

    if not room:
        return None

    room.title = room_data.title
    room.description = room_data.description

    db.commit()
    db.refresh(room)

    return room

def create_question(db: Session, room_id: int, question):
    new_question = Question(
        room_id=room_id,
        title=question.title,
        description=question.description,
        difficulty=question.difficulty
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


def get_questions_by_room(db: Session, room_id: int):
    return (
        db.query(Question)
        .filter(Question.room_id == room_id)
        .all()
    )


def get_question_by_id(db: Session, question_id: int):
    return (
        db.query(Question)
        .filter(Question.id == question_id)
        .first()
    )



def delete_question(db: Session, question_id: int):
    question = get_question_by_id(db, question_id)

    if not question:
        return None

    db.delete(question)
    db.commit()

    return question

def update_question(db: Session, question_id: int, question_data):
    question = get_question_by_id(db, question_id)

    if not question:
        return None

    question.title = question_data.title
    question.description = question_data.description
    question.difficulty = question_data.difficulty

    db.commit()
    db.refresh(question)

    return question

def get_question_by_title_and_room(db: Session, room_id: int, title: str):
    return (
        db.query(Question)
        .filter(
            Question.room_id == room_id,
            Question.title == title
        )
        .first()
    )

def get_question_bank(db: Session):
    return db.query(QuestionBankItem).all()


def get_bank_question_by_title(db: Session, title: str):
    return db.query(QuestionBankItem).filter(QuestionBankItem.title == title).first()


def create_bank_question(db: Session, question):
    new_item = QuestionBankItem(
        title=question.title,
        description=question.description,
        difficulty=question.difficulty
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


def get_code_session_by_room(db: Session, room_id: int):
    return db.query(CodeSession).filter(CodeSession.room_id == room_id).first()


def create_or_update_code_session(db: Session, room_id: int, code_data):
    code_session = get_code_session_by_room(db, room_id)

    if not code_session:
        code_session = CodeSession(
            room_id=room_id,
            code=code_data.code,
            language=code_data.language
        )

        db.add(code_session)
        db.commit()
        db.refresh(code_session)

        return code_session

    code_session.code = code_data.code
    code_session.language = code_data.language

    db.commit()
    db.refresh(code_session)

    return code_session