from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from typing import List

app = FastAPI(title="Bank Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- MySQL Config ----
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root@1234",
    "database": "bank_db"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ---- Pydantic Models ----
class AccountCreate(BaseModel):
    owner_name: str
    initial_deposit: float

class Account(BaseModel):
    id: int
    owner_name: str
    balance: float

class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float

# ---- Routes ----
@app.get("/")
def root():
    return {"message": "Bank Management API is running"}

@app.post("/accounts", response_model=Account)
def create_account(account: AccountCreate):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO accounts (owner_name, balance) VALUES (%s, %s)",
        (account.owner_name, account.initial_deposit)
    )
    db.commit()
    acc_id = cursor.lastrowid
    cursor.close()
    db.close()
    return Account(id=acc_id, owner_name=account.owner_name, balance=account.initial_deposit)

@app.get("/accounts", response_model=List[Account])
def list_accounts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, owner_name, balance FROM accounts")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return [Account(**row) for row in rows]

@app.post("/transfer")
def transfer(req: TransferRequest):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT balance FROM accounts WHERE id=%s FOR UPDATE", (req.from_account_id,))
        from_acc = cursor.fetchone()
        if not from_acc or from_acc["balance"] < req.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds or account not found")

        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE id=%s", (req.amount, req.from_account_id))
        cursor.execute("UPDATE accounts SET balance = balance + %s WHERE id=%s", (req.amount, req.to_account_id))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()

    return {"status": "success", "transferred": req.amount}
