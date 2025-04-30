from fastapi import FastAPI
from .views.book import router

def create_app():
    app = FastAPI(title="Library API with MongoDB")
    app.include_router(router)
    return app