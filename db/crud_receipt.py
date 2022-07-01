from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm.session import Session
from receipt.models import Favourites, Likes, Receipt
from receipt.schemas import ReceiptBase

"""Файл с функциями для операций CRUD рецептов"""


def create_recept(db: Session, request: ReceiptBase, user_id: int, path: Optional[str]):
    """Создание рецепта"""
    receipt = Receipt(
        name = request.name,
        description = request.description,
        cookie_steps = request.cookie_steps,
        image = path,
        dish_type = request.dish_type,
        user_id = user_id,
        hashtags = request.hashtags
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def get_receipt_by_id(db: Session, id: int):
    """Получение рецепта по ID"""
    receipt = db.query(Receipt).filter(Receipt.id == id).first()
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error' : f'receipt with {id} not found'})
    return receipt

def get_receipt_by_user_id(db: Session, user_id: int):
    """Получаем все рецепты пользователя"""
    receipts = db.query(Receipt).filter(Receipt.user_id == user_id).all()
    return receipts


def ban_or_unban_receipt(db: Session, id: int):
    """Для админа, меняет статус у рецепта"""
    receipt = db.query(Receipt).filter(Receipt.id == id)
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error' : f'receipt with {id} not found'})
    if receipt.first().is_active:
        receipt.update({Receipt.is_active: False})
    else:
        receipt.update({Receipt.is_active: True})
    db.commit()
    return 'receipt status is updated'


def update_receipt(db: Session, user_id: int, receipt_id: int, data: ReceiptBase):
    """Обновление рецепта"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id)
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error' : f'receipt with {id} not found'})
    if receipt.one().user_id != user_id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail={'error' : f'You cant modify receipt if u werent create'})
    receipt.update(
        {
        Receipt.name : data.name,
        Receipt.update_date : datetime.now(),
        Receipt.dish_type : data.dish_type,
        Receipt.description : data.description,
        Receipt.cookie_steps : data.cookie_steps,
        Receipt.hashtags : data.hashtags
        }
    )
    db.commit()
    return 'Ur receipt is sucsessfully updated'

def delete_recept(db: Session, user_id: int, receipt_id: int):
    """Удаление рецепта по ID, может удалить только создавший его пользователь"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id)
    if not receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'error' : f'receipt with {id} not found'})
    if receipt.one().user_id != user_id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail={'error' : f'You cant modify receipt if u werent create'})
    receipt.delete()
    db.commit()
    return 'Ur receipt was deleted'

def get_all_receipt(db: Session):
    """Получение всех рецептов"""
    receipts = db.query(Receipt).filter(Receipt.is_active==True).all()
    return receipts


def set_like(db: Session, current_user, receipt_id: int):
    """Поставить или убрать лайк с рецепта"""
    likes = db.query(Receipt).filter(Receipt.id==receipt_id).one().likes
    is_liked = False
    for like in likes:
        if current_user.id == like.user_id: 
            is_liked = True
            break
    
    if is_liked: #если пользователь уже лайкал рецепт, убираем
        like = db.query(Likes).filter(and_(Likes.user_id == current_user.id, Likes.receipt_id == receipt_id))
        like.delete()
        db.commit()
        return 'like was removed'
    else: # иначе - добавляем
        like = Likes(
            user_id = current_user.id,
            receipt_id = receipt_id
        )
        db.add(like)
        db.commit()
        db.refresh(like)
        return 'like was added'
        
def add_to_favourites(db: Session, receipt_id: int, current_user):
    """Добавить или удалить из избранных рецепт"""
    fauvorites = current_user.favourites
    in_favourites = False
    for item in fauvorites:
        if receipt_id == item.receipt_id:
            in_favourites = True
            break
    if in_favourites: # если было в избранном - удаляем
        fauvorite = db.query(Favourites).filter(and_(Favourites.user_id == current_user.id, Favourites.receipt_id == receipt_id))
        fauvorite.delete()
        db.commit()
        return f'Receipt with id {receipt_id} was removed from ur favoutires'
    else: # иначе - добавляем
        fauvorite = Favourites(
            user_id = current_user.id,
            receipt_id = receipt_id
        )
        db.add(fauvorite)
        db.commit()
        db.refresh(fauvorite)
        return f'Receipt with id {receipt_id} was added to ur favoutires'