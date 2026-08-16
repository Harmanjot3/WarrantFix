from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection
import models
import auth
from scheduler import send_twilio_sms
from datetime import datetime
from dateutil.relativedelta import relativedelta
import mysql.connector
import jwt

app = FastAPI(title="WarrantFix API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.on_event("startup")
def startup():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create tables if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone_number VARCHAR(255) NOT NULL
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS offline_product_registrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        product_name VARCHAR(255),
        seller VARCHAR(255),
        purchase_date DATE,
        warranty_period INT,
        warranty_code VARCHAR(255),
        purchase_bill_path VARCHAR(255)
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS online_product_registrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        product_name VARCHAR(255),
        purchase_date DATE,
        warranty_period INT,
        warranty_code VARCHAR(255),
        source_url VARCHAR(255)
    )""")
    conn.commit()
    cursor.close()
    conn.close()

@app.post("/api/register")
def register(user: models.UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_pw = auth.get_password_hash(user.password)
        cursor.execute("INSERT INTO users (username, password, email, phone_number) VALUES (%s, %s, %s, %s)", 
                       (user.username, hashed_pw, user.email, user.phone_number))
        conn.commit()
        return {"message": "User registered successfully"}
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/login")
def login(user: models.UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (user.username,))
        db_user = cursor.fetchone()
        if not db_user or not auth.verify_password(user.password, db_user['password']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = auth.create_access_token(data={"sub": str(db_user['id'])})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        cursor.close()
        conn.close()

@app.get("/api/products")
def get_products(user_id: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM offline_product_registrations WHERE user_id = %s", (user_id,))
        offline = cursor.fetchall()
        cursor.execute("SELECT * FROM online_product_registrations WHERE user_id = %s", (user_id,))
        online = cursor.fetchall()
        
        # Calculate expiry for offline
        for p in offline:
            purchase_date = p['purchase_date']
            p['expiry_date'] = (purchase_date + relativedelta(months=p['warranty_period'])).strftime("%Y-%m-%d")
            p['type'] = 'offline'

        # Calculate expiry for online
        for p in online:
            purchase_date = p['purchase_date']
            p['expiry_date'] = (purchase_date + relativedelta(months=p['warranty_period'])).strftime("%Y-%m-%d")
            p['type'] = 'online'
            
        return {"products": offline + online}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/products/offline")
def add_offline_product(product: models.ProductRegisterOffline, user_id: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO offline_product_registrations (user_id, product_name, seller, purchase_date, warranty_period, warranty_code, purchase_bill_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, product.product_name, product.seller, product.purchase_date, product.warranty_period, product.warranty_code, product.purchase_bill_path))
        conn.commit()
        return {"message": "Offline product registered"}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/products/online")
def add_online_product(product: models.ProductRegisterOnline, user_id: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO online_product_registrations (user_id, product_name, purchase_date, warranty_period, warranty_code, source_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, product.product_name, product.purchase_date, product.warranty_period, product.warranty_code, product.source_url))
        conn.commit()
        return {"message": "Online product registered"}
    finally:
        cursor.close()
        conn.close()

@app.post("/api/reminders")
def set_reminders(req: models.ReminderRequest, user_id: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT phone_number FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        phone = user_data[0]
        
        # Trigger an immediate acknowledgment for demonstration
        send_twilio_sms(f"WarrantFix: Reminders set for every {req.interval_days} days.", phone)
        
        return {"message": "Reminders configured successfully"}
    finally:
        cursor.close()
        conn.close()
