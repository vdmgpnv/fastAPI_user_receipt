import datetime
from typing import List
from pydantic import BaseModel
       
class DishBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

class ReceiptBase(BaseModel):
    name: str
    dish_type: int
    description: str
    cookie_steps: str
    hashtags: str
    
    class Config:
        orm_mode = True
    
    
class ReceiptDisplay(ReceiptBase):
    id: int
    creation_date : datetime.datetime
    is_active: bool
    image: str
    user_id: int