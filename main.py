from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from importlib import import_module

models = import_module(f"{__package__}.models" if __package__ else "models")
database = import_module(f"{__package__}.database" if __package__ else "database")
engine, SessionLocal = database.engine, database.SessionLocal

app = FastAPI(title="Book Management System API")

# Enable CORS for React Frontend (Vite default port: 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    published_year: int = Field(..., gt=0)
    genre: Optional[str] = "General"
    price: Optional[float] = 0.0

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True

# CRUD Endpoints
@app.get("/books", response_model=List[BookResponse])
def fetch_all_books(db: Session = Depends(get_db)):
    return db.query(models.Books).all()

@app.get("/books/{book_id}", response_model=BookResponse)
def fetch_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = models.Books(
        title=book.title,
        author=book.author,
        published_year=book.published_year,
        genre=book.genre,
        price=book.price
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updated_data: BookCreate, db: Session = Depends(get_db)):
    query = db.query(models.Books).filter(models.Books.id == book_id)
    existing_book = query.first()
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")
    query.update(updated_data.model_dump(), synchronize_session=False)
    db.commit()
    return query.first()

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Books).filter(models.Books.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return None


