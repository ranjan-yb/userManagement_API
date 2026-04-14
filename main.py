from fastapi import FastAPI
from app.routes import users
from app.models import user
from app.database import Base, engine

# print("Password type:", type(user.password), "Value:", )

app = FastAPI()

user.Base.metadata.create_all(bind=engine)
app.include_router(users.router)

# @app.get("/")
# def home():
#     print("fast api running successfully ")
#     return "home"
