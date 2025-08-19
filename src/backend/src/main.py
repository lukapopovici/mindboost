from fastapi import FastAPI, UploadFile, File, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import httpx

from . import auth, models, schemas
from .database import SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MindBoost API Gateway")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Service URLs for Docker internal communication
PDF_PARSER_URL = "http://pdf-parser-microservice:8001/parse-pdf/"
BEDROCK_CLIENT_URL = "http://bedrock-client-microservice:8002/invoke-bedrock/"
KNOWLEDGE_GRAPH_URL = "http://knowledge-graph-microservice:8003/knowledge-graph/"

# --- Authentication Endpoints ---

@app.post("/register", response_model=schemas.User, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Protected Endpoints ---

@app.get("/users/me", response_model=schemas.User, tags=["Users"])
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/parse-pdf/", tags=["Core Services"])
async def proxy_parse_pdf(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user)):
    async with httpx.AsyncClient() as client:
        files = {'file': (file.filename, await file.read(), file.content_type)}
        response = await client.post(PDF_PARSER_URL, files=files)
        response.raise_for_status()
        return response.json()

@app.post("/invoke-bedrock/", tags=["Core Services"])
async def proxy_invoke_bedrock(request: Request, current_user: models.User = Depends(auth.get_current_user)):
    data = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(BEDROCK_CLIENT_URL, json=data)
        response.raise_for_status()
        return response.json()
        
@app.post("/knowledge-graph/", tags=["Core Services"])
async def proxy_knowledge_graph(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user)):
    async with httpx.AsyncClient() as client:
        files = {'file': (file.filename, await file.read(), file.content_type)}
        response = await client.post(KNOWLEDGE_GRAPH_URL, files=files)
        response.raise_for_status()
        return response.json()