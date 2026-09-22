from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.users import UserModel, UserType
from models.profiles import ProfileModel
from schemas.users import RegisterRequestSchema, LoginRequestSchema
from auth.jwt_cookie_auth import generate_access_token, generate_refresh_token, decode_refresh_token
from messages.auth import Messages
from core.database import get_db
import secrets


router = APIRouter(tags=["account"], prefix="/api/v1")


@router.post("/register")
async def user_register(request: RegisterRequestSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter_by(email=request.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=Messages.user_already_exists)

    user_obj = UserModel(
        username = request.email.lower(),
        email = request.email.lower(),
        type = UserType.CUSTOMER.value,
        is_active = True
    )
    user_obj.set_password(request.password)

    profile_obj = ProfileModel()
    user_obj.profile = profile_obj

    db.add(user_obj)
    db.commit()

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": Messages.registered_successfully})

@router.post("/login")
async def user_login(request: LoginRequestSchema, db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(username=request.email.lower()).first()
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.Invalid_user_pass)


    if not user_obj.verify_password(request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.Invalid_user_pass)

    access_token = generate_access_token(str(user_obj.id))
    refresh_token = generate_refresh_token(str(user_obj.id))

    csrf_token = secrets.token_urlsafe(32)

    response = JSONResponse(
        content={"detail": Messages.logged_in_successfully}, status_code=status.HTTP_200_OK
    )
    # Set the tokens in the cookies
    response.set_cookie("access_token", access_token,
                        httponly=True, secure=True, samesite="None")
    response.set_cookie("refresh_token", refresh_token,
                        httponly=True, secure=True, samesite="None")
    response.set_cookie("csrf_token", csrf_token,
                        httponly=True, secure=True, samesite="None")
    
    return response


@router.post("/refresh-token")
async def user_refresh_token(request: Request, response: JSONResponse, db: Session = Depends(get_db)):
    
    if refresh_token := request.cookies.get("refresh_token"):
        user_id = decode_refresh_token(refresh_token)
        new_access_token = generate_access_token(user_id)
        response = JSONResponse(
            content={"detail": Messages.token_refreshed}, status_code=status.HTTP_200_OK
        )
        response.set_cookie("refresh_token", new_access_token,
                                httponly=True, secure=True, samesite="None")
        return response

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Messages.refresh_token_not_found)

@router.post("/logout")
def logout():
    response = JSONResponse(content={"detail": Messages.logged_out})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("csrf_token")
    return response