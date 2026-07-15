"""Pydantic schemas for authentication request/response validation."""

from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: Annotated[EmailStr, Field()]
    username: Annotated[str, Field(min_length=3, max_length=32)]
    password: Annotated[str, Field(min_length=6, max_length=128)]


class UserLogin(BaseModel):
    email: Annotated[EmailStr, Field()]
    password: Annotated[str, Field(min_length=1, max_length=128)]


class UserResponse(BaseModel):
    id: int
    email: str
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
