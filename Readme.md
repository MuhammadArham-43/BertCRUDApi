# FastAPI Service for Sentiment Classification

We provide a FastAPI router handling sentiment classification. We use separate Pydantic route validation and Sqlite3 database.

## Database Configuration

We use SqlAlchemy for ORM based database manipulation and use a single model/table to hold our data.

The data model is as follows:

```python
__tablename__ = "reviews"

comment_id = Column(Integer, primary_key=True, index=True)
campaign_id = Column(Integer)
description = Column(String)
sentiment = Column(String, nullable=True)
```

## Setup

```bash
git clone https://github.com/MuhammadArham-43/BertCRUDApi.git
cd BertCRUDApi
```

Setup a python environment, install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Setup environment variables that point to the SqliteDB url and the trained model checkpoint file. We provide a sample env file denoting the required environment variables.

```bash
export DB_URL=<str>
export BERT_CKPT_PATH=<str>
```

Exceute the FastAPI server.

```bash
python3 main.py
```

## Documentation

### Insert

```curl
curl --location --request PUT 'http://0.0.0.0:8080/insert' \
--header 'Content-Type: application/json' \
--data '{
    "comment_id": 1234,
    "campaign_id": 4567,
    "description": "new comment",
    "sentiment": "positive"
}'
```

### Predict

```curl
curl --location 'http://0.0.0.0:8080/predict' \
--header 'Content-Type: application/json' \
--data '{
    "description": "hahahahaha i loved it"
}'
```

### Delete

```curl
curl --location --request DELETE 'http://0.0.0.0:8080/delete' \
--header 'Content-Type: application/json' \
--data '{
    "comment_id": 1234
}'
```

### Update

```curl
curl --location --request PATCH 'http://0.0.0.0:8080/update' \
--header 'Content-Type: application/json' \
--data '{
    "comment_id": "1234",
    "campaign_id": "45678",
    "description": "this is updated text",
    "sentiment": "negative"
}'
```

### Bulk Insert

```curl
curl --location 'http://0.0.0.0:8080/bulk-insert' \
--form 'document=@"/path/to/file"'
```
