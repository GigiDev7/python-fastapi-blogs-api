from fastapi import FastAPI, Depends
import uvicorn
from schemas import Blog
from database import engine, SessionLocal
import models
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield  db
    finally:
        db.close()


app = FastAPI()


@app.get('/')
def get_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/{blog_id}')
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    return blog


@app.post('/')
def create_blog(blog: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=blog.title, body=blog.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


if __name__ == "__main__":
    uvicorn.run(app=app, port=8000)
