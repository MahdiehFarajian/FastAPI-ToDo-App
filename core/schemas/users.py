from pydantic import BaseModel, EmailStr, field_validator
import re
from utils.exceptions import CustomValidationException


class RegisterRequestSchema(BaseModel):
    email: EmailStr = "user@example.com"
    password: str = "A@a1234567"
    password_confirm: str = "A@a1234567"

    @field_validator("password")
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value

    @field_validator("password_confirm")
    def check_passwords_match(cls, password_confirm, validation):
        if not (password_confirm == validation.data.get("password")):
            raise ValueError("passwords doesnt match")
        return password_confirm


class LoginRequestSchema(BaseModel):
    email: EmailStr = "user@example.com"
    password: str = "A@a1234567"

    @field_validator('email', mode='before')
    def validate_email(cls, v):
        if not v:
            raise CustomValidationException("Email is required.")
        return v

    @field_validator('password', mode='before')
    def validate_password(cls, v):
        if not v:
            raise CustomValidationException("Password is required.")
        return v