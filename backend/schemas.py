from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    invite_code: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    title: str
    description: str
    


class RoomResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int

    class Config:
        from_attributes = True


class ParticipantCreate(BaseModel):
    room_id: int


class ParticipantResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    role: str
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class RoomUpdate(BaseModel):
    title: str
    description: str

class QuestionCreate(BaseModel):
    title: str
    description: str
    difficulty: str

class QuestionUpdate(BaseModel):
    title: str
    description: str
    difficulty: str

class QuestionResponse(BaseModel):
    id: int
    room_id: int
    title: str
    description: str
    difficulty: str

    class Config:
        from_attributes = True

class QuestionBankResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: str

    class Config:
        from_attributes = True

class CodeSessionCreate(BaseModel):
    code: str
    language: str


class CodeSessionResponse(BaseModel):
    id: int
    room_id: int
    code: str
    language: str

    class Config:
        from_attributes = True