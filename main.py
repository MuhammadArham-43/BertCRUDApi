from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import SqliteDB, Base
from routers import ReviewAnalysisRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = SqliteDB()
    session = database.get_session()
    session.close()
    Base.metadata.create_all(bind=database.get_engine())
    yield
    
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ReviewAnalysisRouter().router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)    
    