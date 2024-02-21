from sqlalchemy import Column, Integer, String
from database import Base


class Review(Base):
    __tablename__ = "reviews"
    
    comment_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer)
    description = Column(String)
    sentiment = Column(String, nullable=True)

    def __repr__(self):
        return f"<Review(comment_id={self.comment_id}, campaign_id={self.campaign_id}, description={self.description}, sentiment={self.sentiment})>"
