from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None


class UserResponse(UserBase):
    id: int

    model_config = {"from_attributes": True}
