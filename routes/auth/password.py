from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from schemas.auth.auth import ForgotPasswordRequest, ResetPasswordRequest
from models.users.users import Users
from database.db import get_db
from auth.security import create_password_reset_token, verify_password_reset_token, hash_password
from config import settings, PASSWORD_RESET_TEMPLATE
from utils.email import send_email
import logging

router = APIRouter(prefix="/auth", tags=["Password"])


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        result = await db.execute(select(Users).filter(Users.email == data.email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        token = create_password_reset_token(user.email)
        reset_url = settings.PASSWORD_RESET_URL.format(token=token)

        html_content = PASSWORD_RESET_TEMPLATE.format(
            reset_url=reset_url,
            expire_hours=(settings.RESET_PASSWORD_TOKEN_EXPIRE_HOURS / 60 ) * 5 # Convert hours to minutes
        )

        send_email(
            to_email=user.email,
            subject="Reset Your Password",
            html_content=html_content
        )

        return {"message": "Password reset link sent to your email."}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error during forgot-password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the forgot password request."
        )


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        email = verify_password_reset_token(data.token)

        result = await db.execute(select(Users).filter(Users.email == email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.password = hash_password(data.new_password)
        await db.commit()

        return {"message": "Password has been reset successfully."}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error during reset-password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resetting the password."
        )
