from typing import List
from .schemas import Receipt, UserDisplay, UserBase, UserChangeNN
from db import crud_user, crud_receipt
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from db.database import get_db
from .models import User
from .hash import Hash
from user import oauth2

router = APIRouter(
    tags=['user']
)


@router.post('/user/create', response_model=UserDisplay)
def create_user(request: UserBase,
                db: Session = Depends(get_db)):
    """Эндпоинт создания пользователя"""
    return crud_user.create_user(db, request)


@router.post('/token')
def get_token(request: OAuth2PasswordRequestForm = Depends(),
              db: Session = Depends(get_db)):
    """Эндпоинт создания токена для юзера, по которому можно проходить авторизацию"""
    
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Invalid credentials')
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Incorrect password')  
    access_token = oauth2.create_access_token(data={'sub': user.username})
    return {
        'access_token' : access_token,
        'token_type' : 'bearer',
        'user_id' : user.id,
        'username' : user.username
    }
    
    
@router.get('/user/get_user', response_model=UserDisplay)
def get_user_data(current_user: UserBase = Depends(oauth2.get_correct_user),
                  db: Session = Depends(get_db)):
    """Для авторизованных пользователей, получение своего профиля"""
    return current_user
    
@router.get('/user/get_first_ten_users', response_model=List[UserDisplay])
def get_users_data(db: Session = Depends(get_db),
                   current_user: UserBase = Depends(oauth2.get_correct_user)): 
    """Получение первых 10 пользователей, отсортированных по кол-ву рецептов"""
    return crud_user.get_first_ten_users(db=db)


@router.put('/admin/ban_user/{id}')
async def ban_user(id: int, db: Session = Depends(get_db),
             current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Для админа, эндпоинт для блокировки пользователя"""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='sorry, you need to be admin if u want to ban user')
    return crud_user.ban_or_unbad_user(db, id)


@router.put('/admin/unban_user/{id}', summary='unban user')
async def unban_user(id: int, db: Session = Depends(get_db),
             current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Для админа, эндпоинт для разблокировки пользователя"""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='sorry, you need to be admin if u want to unban user')
    return crud_user.ban_or_unbad_user(db, id)


@router.post('/user/update_nickname')
async def update_nickname(request: UserChangeNN,
                    db: Session = Depends(get_db),
             current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Для авторизованного пользователя, смена его ник-нейма"""
    return crud_user.update_nickname(db, current_user.id, request)


@router.delete('/user/delete')
async def delete_user(db: Session = Depends(get_db),
                current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Удаление пользователя."""
    return crud_user.delete_user(db ,current_user.id)

@router.get('/user/fauvorites', response_model=List[Receipt])
async def get_fauvorites(db: Session = Depends(get_db),
                current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Получение ID-шников избранных рецептов"""
    
    return crud_user.get_fauvorites(db, current_user)
    