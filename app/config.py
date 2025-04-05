import os

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "0987")
DB_NAME = os.getenv("POSTGRES_DB", "library_db")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = "5432"

SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
