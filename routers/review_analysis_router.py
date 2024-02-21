from fastapi import APIRouter, Depends, HTTPException
from models.pydantic_models import (
    ReviewInputParameters, 
    ReviewDeleteParameters,
    PredictParameters,
    BulkInsertInputParameters
)
from sqlalchemy.exc import IntegrityError
from database import SqliteDB
from models import Review
from classifier import get_classifier_model
from utils.envvars import get_bert_ckpt_path
import pandas as pd
import chardet
from tqdm import tqdm


db_connection = SqliteDB()

class ReviewAnalysisRouter(APIRouter):
    def __init__(self):
        super().__init__()
        
        self.router = APIRouter()
        self.db_connection = SqliteDB()
        self.bert_model = get_classifier_model(
            ckpt_path=get_bert_ckpt_path()
        )
        
        self.router.add_api_route("/", self.test, methods=["GET"])
        self.router.add_api_route("/insert", self.add_review, methods=["PUT"])
        self.router.add_api_route("/predict", self.predict, methods=["POST"])
        self.router.add_api_route("/delete", self.delete_review, methods=["DELETE"])
        self.router.add_api_route("/update", self.update_review, methods=["PATCH"])
        self.router.add_api_route("/bulk-insert", self.bulk_insert, methods=["POST"])
        
    def test(self):
        return {"health": "ok"}

    def add_review(self, input_data: ReviewInputParameters, db = Depends(db_connection.get_db)):
        exists = db.query(Review).get(input_data.comment_id)
        if exists:
            raise HTTPException(status_code=409, detail=f"Entry with comment id {input_data.comment_id} already exists.")
        
        try:
            review = Review(**input_data.dict())
            db.add(review)
            db.commit()
            db.close()
        except:
            raise HTTPException(status_code=422, detail="Error inserting into database")

        return {"success": True}
    
    def predict(self, input_data: PredictParameters):
        prediction = self.bert_model.predict(input_data.description)
        return {
            "prediction": prediction
        }
    
    def delete_review(self, input_data: ReviewDeleteParameters, db = Depends(db_connection.get_db)):
        review = db.query(Review).filter(Review.comment_id == input_data.comment_id).first()
        if review is None:
            raise HTTPException(status_code=404, detail=f"Review with comment id {input_data.comment_id} does not exist")

        db.delete(review)
        db.commit()
        return {"success": True}
    
    def update_review(self, input_data: ReviewInputParameters, db = Depends(db_connection.get_db)):
        review = db.query(Review).filter(Review.comment_id == input_data.comment_id).first()
        if review is None:
            raise HTTPException(status_code=404, detail=f"Review with comment id {input_data.comment_id} does not exist")

        for key, value in input_data.model_dump().items():
            setattr(review, key, value)
        
        db.commit()
        return {
            "success": True
        }
    
    
    
    async def bulk_insert(self, input_data: BulkInsertInputParameters = Depends(), db = Depends(db_connection.get_db)):
    
        def get_encoding(chunk):
            return chardet.detect(chunk)['encoding']
    
        _file = input_data.document
        if not _file.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail="Document must be .csv type")
        
        required_columns = ["comment_id", "campaign_id", "description"]    
        
        df = pd.read_csv(_file.file, encoding="utf-8", header=0)
        
        if not set(required_columns).issubset(df.columns):
            missing_columns = list(set(required_columns) - set(df.columns))
            raise HTTPException(status_code=400, detail=f"Missing columns: {missing_columns}")

        errors = []
        for index, row in tqdm(df.iterrows()):
            comment_id = row["comment_id"]
            campaign_id = row["campaign_id"]
            description = row["description"]

            sentiment = self.bert_model.predict(description)

            try:
                new_review = Review(comment_id=comment_id, campaign_id=campaign_id, description=description, sentiment=sentiment)
                db.add(new_review)
                db.commit() 
            except Exception as e:
                db.rollback()
                errors.append({"comment_id": comment_id, "error": str(type(e))})

        if len(errors) > 0:
            raise HTTPException(status_code=400, detail={"errors": errors})
        
        return {"message": "Bulk insert successful"}