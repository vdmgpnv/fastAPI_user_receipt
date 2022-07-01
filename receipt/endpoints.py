import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from db.database import get_db
from db import crud_receipt
from user import oauth2
from user.schemas import UserBase
from .schemas import ReceiptBase, ReceiptDisplay
from sqlalchemy.orm.session import Session
from fastapi_pagination import Page, paginate


router = APIRouter(
    tags=['receipts']
)


@router.post('/receipts/add')
def create_receipt(request: ReceiptBase = Depends(),
                   db: Session = Depends(get_db),
                   current_user: UserBase = Depends(oauth2.get_correct_user),
                   img: UploadFile = File(...)):
    """Метод для создания рецепта, в качестве типа блюда передается ид
    1 - Салат
    2 - Первое
    3 - второе
    4 - Напиток
    5 - Выпечка \n
    Если пользователь не авторизован или забанен - нельзя добавить"""
    if not current_user.is_active:
         raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Sorry, you are banned')  
    path = f'media/{img.filename}'
    with open(path, 'w+b') as buffer:
        shutil.copyfileobj(img.file, buffer)  
    return crud_receipt.create_recept(db, request, current_user.id, path)


@router.get('/receipts/all', response_model=Page[ReceiptDisplay])
def get_all_reseipts(db: Session = Depends(get_db),
                     current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Метод для получения всех ид с пагинацией, фильтры не успел добавить("""
    return paginate(crud_receipt.get_all_receipt(db))


@router.get('/receipts/{id}')
def get_the_receipt(id: int, db: Session = Depends(get_db),
                    current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Получаем рецепт по ID, если пользователь забанен, выскакивает исключение"""
    if not current_user.is_active:
         raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Sorry, you are banned')
    return crud_receipt.get_receipt_by_id(db, id)


@router.patch('/admin/ban_receipt/{id}')
async def ban_receipt(id: int, db: Session = Depends(get_db),
             current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Эндпоинт для блокировки рецепта, доступ только у админа"""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='sorry, you need to be admin if u want to ban receipt')
    return crud_receipt.ban_or_unban_receipt(db, id)


@router.patch('/admin/unban_receipt/{id}')
async def unban_receipt(id: int, db: Session = Depends(get_db),
             current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Эндпоинт для разблокировки рецепта, доступ только у админа"""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='sorry, you need to be admin if u want to unban receipt')
    return crud_receipt.ban_or_unban_receipt(db, id)


@router.patch('/receipts/update_receipt/{id}')
async def update_user_receipts(id: int,
                         data: ReceiptBase,
                         db: Session = Depends(get_db),
                         current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Обновление рецепта пользователя, доступ только у авторизованного пользователя, если он не забанен"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Sorry, you are banned')
    return crud_receipt.update_receipt(db, current_user.id, id, data)


@router.delete('/receipts/delete_receipt/{id}')
async def delete_recept(id: int,
                  db: Session = Depends(get_db),
                  current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Удаление рецепта пользователем, если он не забанен"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Sorry, you are banned')
    return { 'message' : crud_receipt.delete_recept(db, current_user.id, id)}


@router.post('/receipts/{id}/set_like')
async def set_like(id: int,
             db: Session = Depends(get_db),
             current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Поставить или снять лайк с рецепта, доступ только у авторизованных пользователей, если они не забаненны"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Sorry, you are banned')
    
    return {'message' : crud_receipt.set_like(db, current_user, id)}
    

@router.post('/receipts/{id}/add_to_favourites')
async def add_to_favourites(id: int,
             db: Session = Depends(get_db),
             current_user: UserBase = Depends(oauth2.get_correct_user)):
    """Добавление рецепта в избранное, доступ только у авторизованных пользователей, которые не забанены"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Sorry, you are banned')
    
    return { 'message' : crud_receipt.add_to_favourites(db, id, current_user)}