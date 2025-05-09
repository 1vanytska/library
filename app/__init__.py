from fastapi import FastAPI
from .views import book, auth

def create_app():
    app = FastAPI(title="Library API with MongoDB")
    app.include_router(book.router)
    app.include_router(auth.router)
    return app