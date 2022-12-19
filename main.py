from fastapi import FastAPI, Depends, status, Response, HTTPException
import uvicorn
from schemas import Blog, ShowBlog, User, UserResponse
from database import engine, SessionLocal
import models
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield  db
    finally:
        db.close()


app = FastAPI()


@app.get('/', response_model=List[ShowBlog], tags=['blogs'])
def get_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/{blog_id}', response_model=ShowBlog, tags=['blogs'])
def get_blog(blog_id: int, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog does not exist with that {blog_id}")
    return blog


@app.delete('/{blog_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['blogs'])
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == blog_id).delete(synchronize_session=False)
    db.commit()
    return


@app.put('/{blog_id}', status_code=status.HTTP_202_ACCEPTED, tags=['blogs'])
def update_blog(blog_id: int, request: Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found')
    blog.update({"title": request.title, "body": request.body}, synchronize_session=False)
    db.commit()
    return 'updated'


@app.post('/', status_code=status.HTTP_201_CREATED, tags=['blogs'])
def create_blog(blog: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=blog.title, body=blog.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated="auto")


@app.post('/user', response_model=UserResponse, tags=['users'])
def create_user(request: User, db: Session = Depends(get_db)):
    hashed_password = pwd_ctx.hash(request.password)
    new_user = models.User(name=request.name, email=request.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get('/user/{user_id}', response_model=UserResponse, tags=['users'])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    return user


if __name__ == "__main__":
    uvicorn.run(app=app, port=8000)
