from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime



class CreateUser(SQLModel):
    username:str
    email: Optional[str]
    password:str

class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: Optional[str]
    hashed_password: str

class LoginUser(SQLModel):
    username:  str
    password: str

class UserPublic(SQLModel):
    id: int
    username: str
    email: str

class recipes(SQLModel, table= True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ingredients: str
    steps: str
    image_url: Optional[str] = None
    is_draft: Optional[bool] = Field(default=True)
    is_ai_generated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="users.id")


class CreateRecipe(SQLModel):
    name: str
    ingredients: str
    steps: str

class ShowRecipe(SQLModel):
    id: int
    name: str
    user_id: int = Field(foreign_key="users.id")
    ingredients: str
    steps: str
    image_url: Optional[str] = None


class UpdateRecipe(SQLModel):
    name: Optional[str] = None
    ingredients: Optional[str] = None
    steps: Optional[str] = None

class RecipeImage(SQLModel):
    name: str
    image_url: str


