from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    member_name = Column(String(255), nullable=False)
    facility = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    date_submitted = Column(Date)