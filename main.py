from fastapi import FastAPI
from app.routes import users
from app.models import user
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

user.Base.metadata.create_all(bind=engine)
app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


