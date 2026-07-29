from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    member_name = Column(String, nullable=False)
    facility = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    date_submitted = Column(Date)