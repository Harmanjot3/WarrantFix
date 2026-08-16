from pydantic import BaseModel
from typing import Optional
from datetime import date

class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    phone_number: str

class UserLogin(BaseModel):
    username: str
    password: str

class ProductRegisterOffline(BaseModel):
    product_name: str
    seller: str
    purchase_date: date
    warranty_period: int
    warranty_code: str
    purchase_bill_path: str

class ProductRegisterOnline(BaseModel):
    product_name: str
    purchase_date: date
    warranty_period: int
    warranty_code: str
    source_url: str

class ReminderRequest(BaseModel):
    interval_days: int
