from datetime import date
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, get_db, Base
from models import Claim

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClaimCreate(BaseModel):
    member_name: str
    facility: str
    amount: float

class ClaimStatusUpdate(BaseModel):
    status: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/claims")
def list_claims(db: Session = Depends(get_db)):
    return db.query(Claim).all()

@app.post("/claims")
def create_claim(claim: ClaimCreate, db: Session = Depends(get_db)):
    new_claim = Claim(
        member_name=claim.member_name,
        facility=claim.facility,
        amount=claim.amount,
        status="pending",
        date_submitted=date.today()
    )
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    return new_claim

@app.patch("/claims/{claim_id}")
def update_status(claim_id: int, update: ClaimStatusUpdate, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    claim.status = update.status
    db.commit()
    db.refresh(claim)
    return claim

@app.delete("/claims/{claim_id}")
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    db.delete(claim)
    db.commit()
    return {"result": "deleted"}