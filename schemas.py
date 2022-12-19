from pydantic import BaseModel


class Blog(BaseModel):
    title: str
    body: str

class User(BaseModel):
    email: str
    password: str
    name: str

class ShowBlog(BaseModel):
    title:str
    body:str
    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    name: str
    email: str

    class Config:
        orm_mode = True
