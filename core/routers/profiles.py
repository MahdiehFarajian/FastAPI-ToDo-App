from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.users import UserModel
from models.profiles import ProfileModel
from auth.jwt_cookie_auth import get_authenticated_user
import models.listeners
from messages.profiles import Messages
from schemas.profiles import ProfileResponseSchema, ProfileUpdateSchema

router = APIRouter(tags=["profile"], prefix="/api/v1")


@router.get("/profile", response_model=ProfileResponseSchema, status_code=status.HTTP_200_OK)
def retrieve_or_create_profile(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    profile = db.query(ProfileModel).filter_by(user_id=user.id).first()
    if not profile:
        profile = ProfileModel(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("/profile/edit", status_code=status.HTTP_200_OK)
def update_profile(
    request: ProfileUpdateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user),
):
    profile = db.query(ProfileModel).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=Messages.profile_not_found)

    # Update only fields provided in request
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    
    # Mark user's profile as completed
    user.is_profile_complete = True
    db.commit()
    db.refresh(profile)
    db.refresh(user)

    # Convert profile model to dict and add detail message
    profile_data = {column.name: getattr(profile, column.name) for column in profile.__table__.columns}
    profile_data["detail"] = Messages.profile_updated_successfully
    profile_data["email"] = user.email 
    return {"detail": Messages.profile_updated_successfully}