from fastapi import FastAPI, Depends,HTTPException, status, Header
from auth_utils import hash_password,verify_password,create_access_token,decode_access_token
from models import Users, CreateUser, LoginUser, UserPublic,CreateRecipe,ShowRecipe, recipes, UpdateRecipe, RecipeImage
from database import create_db_and_tables, SessionDep
from sqlmodel import select, Field, Relationship
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials, OAuth2PasswordBearer
from recipe_utils import client, generate_recipe_image_payload, generate_image_url
import os
from dotenv import load_dotenv

 
app = FastAPI()
security = HTTPBearer()

def get_current_user( session:SessionDep, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail="Creds Missing")
    token = credentials.credentials

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Autorized")
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    account = session.exec(select(Users).where(Users.username == username)).first()
    if account is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return account


@app.get("/")
def root():
    return {"message":"Hello World"}

@app.post("/signup")
def signup(session: SessionDep, userdata: CreateUser):
    statement = select(Users).where(Users.username == userdata.username)

    existing_account = session.exec(statement).first()

    if existing_account:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pwd_string = hash_password(userdata.password)
    new_account = Users(username=userdata.username, email=userdata.email,hashed_password=hashed_pwd_string)
    session.add(new_account)
    session.commit()
    session.refresh(new_account)

    return {"username": userdata.username}

@app.post("/login")
def login(session: SessionDep, userdata:LoginUser):
    statement = select(Users).where(Users.username == userdata.username)
    existing_account = session.exec(statement).first()

    if not existing_account or not verify_password(userdata.password, existing_account.hashed_password):
        raise HTTPException(status_code=400, detail="User not found")
    
    access_token = create_access_token(data={"sub":existing_account.username})
    return{"access_token":access_token, "token_type":"bearer", "user":UserPublic.from_orm(existing_account)}


@app.post("/recipes", response_model=ShowRecipe)
def create_new_recipe(session:SessionDep, recipe:CreateRecipe, current_user: Users = Depends(get_current_user)):
    new_recipe = recipes(**recipe.model_dump(), user_id=current_user.id)
    session.add(new_recipe)
    session.commit()
    session.refresh(new_recipe)
    return new_recipe

@app.get("/recipes", response_model=list[ShowRecipe])
def show_all_recipes(session:SessionDep, offset: int = 0, limit:int = 5, current_user: Users = Depends(get_current_user)):
    all_recipes = session.exec(select(recipes).offset(offset).limit(limit)).all()
    return all_recipes

@app.get("/recipes/{recipe_id}", response_model=ShowRecipe)
def show_recipe(session:SessionDep, recipe_id: int, current_user: Users = Depends(get_current_user)):
    recipe = session.get(recipes, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@app.patch("/recipes/{recipe_id}", response_model=ShowRecipe)
def update_recipe(session:SessionDep, recipe_id: int, recipe_update: UpdateRecipe, current_user: Users = Depends(get_current_user)):
    recipe = session.get(recipes, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if current_user.id != recipe.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this recipe")
    
    recipe_data = recipe_update.model_dump(exclude_unset=True)
    recipe.sqlmodel_update(recipe_data)
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@app.delete("/recipes/{recipe_id}")
def delete_recipe(session:SessionDep, recipe_id:int, current_user: Users = Depends(get_current_user)):
    recipe = session.get(recipes, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if current_user.id != recipe.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this recipe")
    
    session.delete(recipe)
    session.commit()
    return{"ok":True}

@app.get("/recipes/{recipe_id}/image")
def show_recipe_image(session: SessionDep, recipe_id:int,current_users: Users = Depends(get_current_user)):
    recipe = session.get(recipes, recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return {"name":recipe.name, "link":recipe.image_url}


@app.post("/recipes/{recipe_id}/generate-image")
def generate_recipe_image(session:SessionDep, recipe_id: int, current_users: Users = Depends(get_current_user)):
    recipe = session.get(recipes, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    if recipe.user_id != current_users.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to generate an image for this recipe")
    
    if recipe.image_url:
        raise HTTPException(status_code=404, detail="Recipe Image Exists")
    try:
        dynamic_data = {
            'vessel': 'artisanal ceramic plate',
            'visual_desc': 'richly colored, textured food, elegantly plated',
            'garnishes': 'fresh herbs, scattered spices',
            'ingredients_prop': 'folds of steam, a few scattered ingredients'
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to extract visual details: {str(e)}")

    final_image_prompt = generate_recipe_image_payload(
        recipe_data={'name': recipe.name, 'ingredients': recipe.ingredients},
        dynamic_data=dynamic_data
    )
    

    try:
        # image_url = call_nano_banana_api(final_image_prompt)
        image_url = generate_image_url(final_image_prompt) # MOCK
    except Exception as e:
        # Handle failure if the image generation API call fails
        raise HTTPException(status_code=503, detail=f"Image generation failed: {str(e)}")
    
    recipe.image_url = image_url # Assuming your Recipe model has an 'image_url' column
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return {"image_url": image_url}
