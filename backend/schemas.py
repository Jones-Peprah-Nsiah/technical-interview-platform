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


class RoomResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes = True
        from_attributes = True

