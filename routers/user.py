from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from models import Users
from database import SessionLocal
from routers.auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


# yields a DB session per request, and closes it when the request is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Depends: injects get_db() into each route so we don't manually manage the session
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserVerificationRequest(BaseModel):
    password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user_model


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,
    db: db_dependency,
    user_verification_request: UserVerificationRequest,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(
        user_verification_request.password, user_model.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # payload
    user_model.hashed_password = bcrypt_context.hash(
        user_verification_request.new_password
    )
    db.add(user_model)
    db.commit()

    return {"message": "Password changed successfully"}


@router.put("/change-phone-number", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    user: user_dependency, db: db_dependency,    phone_number: str
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_model.phone_number = phone_number
    db.add(user_model)
    db.commit()

    return {"message": "Phone number changed successfully"}
