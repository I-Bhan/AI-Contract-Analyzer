from pydantic import BaseModel, EmailStr, Field

class RegisterData(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

class LoginData(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)