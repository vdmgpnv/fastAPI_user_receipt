from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from receipt.models import Receipt
from user.hash import Hash
from user.models import User
from user.schemas import UserBase, UserChangeNN



def create_user(db: Session, request: UserBase):
    """Создание нового пользователя, пароль шифруется перед занесением в БД"""
    new_user = User(
        username = request.username,
        password = Hash.bcrypt(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_username(db: Session, username: str):
    """Получение юзера по никнейму, нужно для авторизации"""
    user = db.query(User).filter(User.username == username).outerjoin(Receipt).one()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error' : f'user with {username} not found'})
    user.receipts_count = len(user.receipts)
    return user

def get_first_ten_users(db: Session):
    """Получение первых десяти незаблокированных пользователей, отсортированных по кол-ву рецептов"""
    users = db.query(User).filter(User.is_active == True).outerjoin(Receipt).group_by(User.id).order_by(func.count().desc())[:10]
    for user in users:
        user.receipts_count = len(user.receipts)
    return users

def ban_or_unbad_user(db: Session, user_id: int):
    """Для админа, сменить статус пользователя"""
    user = db.query(User).filter(User.id == user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error' : f'user with {id} not found'})
    if user.first().is_active:
        user.update({User.is_active: False})
    else:
        user.update({User.is_active: True})
    db.commit()
    return 'user status is updated'

def update_nickname(db: Session, id: int, request: UserChangeNN):
    """Смена никнейма пользователя"""
    user = db.query(User).filter(User.id == id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error' : f'user with {id} not found'})
    user.update({
        User.username : request.username,
        User.update_date : datetime.now()
    })
    db.commit()
    return f'Ur username changed to {request.username} sucsessfully'
    
    
def delete_user(db: Session, user_id):
    """Удаление пользователя самим сабой"""
    user = db.query(User).filter(User.id == user_id)
    user.delete()
    db.commit()
    return 'U was deleted'


def get_fauvorites(db: Session, current_user):
    """Получение списка избранных рецептов"""
    favourites = current_user.favourites
    return favourites
    