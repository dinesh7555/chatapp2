from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app import models, schemas, auth 

from app.neo4j_db import neo4j_db
from app.chat import router as chat_router

from fastapi.middleware.cors import CORSMiddleware

# Create tables in MySQL

app = FastAPI()
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)
app.include_router(chat_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
def register(user: schemas.UserRegister,db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
       )
    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.post("/login", response_model=schemas.TokenResponse)
def login(user: schemas.UserLogin,db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if not db_user :
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )
    if not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Invalid password"
        )
    token = auth.create_access_token(
    {"sub": str(db_user.id)}
    )
    return {
       "access_token": token,
        "token_type": "bearer"
    }



from app.auth import get_current_user
@app.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_email": current_user.email
    }


@app.get("/neo4j-test")
def neo4j_test():
    query = "RETURN 'Neo4j connected successfully' AS message"
    result = neo4j_db.run_query(query)
    return result
