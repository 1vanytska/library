from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.db import db
from app.models.user_model import User, UserInDB
from app.models.token_model import RefreshTokenRequest, Token, TokenData, AccessTokenOnly
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_user(username: str) -> Optional[UserInDB]:
    user_data = await db.users.find_one({"username": username})
    if user_data and "hashed_password" in user_data:
        user_data.pop("_id", None)
        return UserInDB(**user_data)
    return None

def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return TokenData(sub=username)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token)
    user = await get_user(token_data.sub)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@router.post("/register", status_code=201)
async def register_user(user: User):
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    await db.users.insert_one({
        "username": user.username,
        "hashed_password": hashed_password
    })

    return {"message": "User registered successfully"}

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/refresh-token", response_model=AccessTokenOnly)
async def refresh_access_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=404, detail="Token is invalid")
        access_token = create_access_token(data={"sub": username})
        return AccessTokenOnly(access_token=access_token, token_type="bearer")
    except JWTError:
        raise HTTPException(status_code=403, detail="Token expired or invalid")
