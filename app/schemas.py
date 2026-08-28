from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re
import uuid


def _normalize_email(value: EmailStr) -> str:
    email = str(value).strip().lower()
    domain = email.rsplit("@", 1)[-1]
    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    if "." not in domain or len(tld) < 2 or " " in email:
        raise ValueError("Please enter a valid email address")
    return email


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=120)
    preferred_hour: int = Field(default=7, ge=6, le=10)

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: EmailStr) -> str:
        return _normalize_email(value)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must include at least one letter and one number")
        return value

    @field_validator("full_name")
    @classmethod
    def name_must_be_clean(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Please enter your name")
        return cleaned


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: EmailStr) -> str:
        return _normalize_email(value)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    preferred_hour: int
    is_active: bool
    totp_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: EmailStr) -> str:
        return _normalize_email(value)

    @field_validator("code")
    @classmethod
    def code_must_be_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Enter the 6-digit code from your email")
        return value


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, value: EmailStr) -> str:
        return _normalize_email(value)


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must include at least one letter and one number")
        return value
