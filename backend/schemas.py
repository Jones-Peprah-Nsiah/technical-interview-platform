from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    title: str
    description: str
    user_id: int


class RoomResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int

    class Config:
        from_attributes = True


class ParticipantCreate(BaseModel):
    user_id: int
    room_id: int


class ParticipantResponse(BaseModel):
    id: int
    user_id: int
    room_id: int

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str