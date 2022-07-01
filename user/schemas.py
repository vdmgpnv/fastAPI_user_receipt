from typing import List, Optional
from pydantic import BaseModel

    

class Receipt(BaseModel):
    id: int
    class Config:
        orm_mode = True   

class UserBase(BaseModel):
    username: str
    password: str
    

class UserDisplay(BaseModel):
    id: int
    username: str
    receipts_count: int = 0
    is_active: bool
    class Config:
        orm_mode = True


class UserChangeNN(BaseModel):
    username: str
    class Config:
        orm_mode = True        
        
        
