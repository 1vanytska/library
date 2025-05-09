from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    username: str
    hashed_password: str