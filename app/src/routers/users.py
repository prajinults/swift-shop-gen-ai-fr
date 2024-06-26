import logging
from typing import List,Annotated

from fastapi import APIRouter, Request, HTTPException, UploadFile, Depends

from sqlalchemy.orm import Session


from ..domain.user import service, schemas
from ..dependencies import validate_access_token, validate_permissions


router = APIRouter(tags=["users"])

@router.post("/users/", response_model=schemas.User, dependencies=[Depends(validate_access_token),Depends(validate_permissions)])
def create_user(user: schemas.UserCreate, request: Request):
    db: Session = request.state.db
    db_user = service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return service.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.User], dependencies=[Depends(validate_access_token),Depends(validate_permissions)])
def read_users(request: Request, skip: int = 0, limit: int = 100):
    db: Session = request.state.db
    users = service.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(validate_access_token),Depends(validate_permissions)])
def read_user(user_id: int, request: Request):
    db: Session = request.state.db
    db_user = service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.post("/users/{user_id}/add-face", response_model=dict, dependencies=[Depends(validate_access_token),Depends(validate_permissions)])
async def add_face(user_id: int, request: Request,file: UploadFile):
    logging.warning(f"Adding face to user {user_id}")
    logging.warning(f"File Size: {file.size}")
    logging.warning(f"File Name: {file.filename}")
    db: Session = request.state.db
    db_user = service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    logging.warning(f"User found: {db_user.email}")
    await service.add_user_face(db=db, file=file, user_id=user_id)
    return {"message": "Face added successfully"}


