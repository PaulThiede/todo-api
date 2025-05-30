from fastapi import HTTPException, APIRouter, status, Depends, Security, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from typing import Annotated
from datetime import timedelta, datetime
from math import ceil

from .models import Item, User
from .schemas import CreateItemRequest, CreateUserRequest, UpdateItemRequest, UpdateUserRequest, ItemRead
from .db import get_db
from .auth import authenticate_user, create_access_token, get_current_user, oauth2_bearer
from util.sort_parser import parse_sorting


router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


# Als Item noch ein String war: # curl.exe -X POST "http://localhost:8000/items?item=orange"
# curl.exe -X POST -H "Content-Type: application/json" -d '{\"title\":\"Leetcode\", \"description\":\"Binary Search\"}' 'http://localhost:8000/items'

'''
          _    _ _______ _    _ 
     /\  | |  | |__   __| |  | |
    /  \ | |  | |  | |  | |__| |
   / /\ \| |  | |  | |  |  __  |
  / ____ \ |__| |  | |  | |  | |
 /_/    \_\____/   |_|  |_|  |_|
                                
                                
'''


@router.get("/login", status_code=status.HTTP_200_OK)
def user(user: user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed.")
    
    new_token = create_access_token(
            user_id = user["id"],
            token_version = user["token_version"],
            expires_delta = timedelta(minutes=20)
        )
    
    return new_token

@router.post("/token") # curl.exe -X POST -H "Content-Type: application/json" -d '{\"title\":\"apple\"}' 'http://localhost:8000/items'
def login_for_username(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
    token = create_access_token(user.id, user.token_version, timedelta(minutes=20))

    return token


'''
  _____ _______ ______ __  __  _____ 
 |_   _|__   __|  ____|  \/  |/ ____|
   | |    | |  | |__  | \  / | (___  
   | |    | |  |  __| | |\/| |\___ \ 
  _| |_   | |  | |____| |  | |____) |
 |_____|  |_|  |______|_|  |_|_____/ 
                                     
                                     
'''

@router.post("/items") # Create New Item
def create_items(item: CreateItemRequest, jwt: Annotated[str, Security(oauth2_bearer)], db: Session = Depends(get_db)):
    user = get_current_user(jwt, db)

    item = Item.create(
        title=item.title,
        user_id=user["id"],
        description=item.description
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/items", response_model=list[ItemRead])
def list_items(
    jwt: Annotated[str, Security(oauth2_bearer)],
    page: int = 1,
    limit: int = 10,
    sort: str = None,
    order: str = None,
    title: str = None,
    description: str = None,
    is_done: bool = None,
    created_since: datetime = None,
    created_until: datetime = None,
    db: Session = Depends(get_db),
):
    user = get_current_user(jwt, db)

    query = db.query(Item).filter(Item.user_id == user["id"])

    if title:
        query = query.filter(Item.title.contains(title))
    if description:
        query = query.filter(Item.description.contains(description))
    if is_done is not None:
        query = query.filter(Item.is_done == is_done)
    if created_since:
        query = query.filter(Item.created_at >= created_since)
    if created_until:
        query = query.filter(Item.created_at <= created_until)

    field_map = {
        "title": Item.title,
        "description": Item.description,
        "created_at": Item.created_at
    }

    try:
        sorting_criteria = parse_sorting(sort, order, field_map)
        if sorting_criteria:
            query = query.order_by(*sorting_criteria) # Der Stern-Operator * entpackt eine Liste oder ein anderes iterierbares Objekt und übergibt dessen Inhalte als einzelne Argumente an eine Funktion.
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


    total_items = query.count()

    if total_items == 0:
        return []

    total_pages = ceil(total_items / limit) if limit else 1
    page = max(1, min(page, total_pages))

    items = query.offset((page - 1) * limit).limit(limit).all()

    return items

    

@router.get("/items/{item_id}", response_model=ItemRead) # Get specific item
def get_item(jwt: Annotated[str, Security(oauth2_bearer)], item_id: int = 0, db: Session = Depends(get_db)) -> Item:
    user = get_current_user(jwt, db)
    items = db.query(Item).filter(Item.user_id == user["id"])

    if item_id < len(items):
        return items[item_id]
    raise HTTPException(status_code=404, detail=f"Item index {item_id} out of bounds for length {len(items)}.")


@router.put("/items/modify") # Modify Item Details
def modify_item(item: UpdateItemRequest, jwt: Annotated[str, Security(oauth2_bearer)], db: Session = Depends(get_db)):
    jwt_user = get_current_user(jwt, db)
    items = db.query(Item).filter(Item.user_id == jwt_user["id"]).all()

    if item.id >= len(items):
        raise HTTPException(status_code=404, detail=f"Item index {item.id} out of bounds for length {len(items)}.")

    db_item = items[item.id]

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.title = item.title if item.title is not "" and item.title is not None else db_item.title
    db_item.description = item.description if item.description is not "" and item.description is not None else db_item.description
    db_item.is_done = item.is_done if item.is_done is not "" and item.is_done is not None else db_item.is_done

    db.commit()
    db.refresh(db_item)

    return db_item


@router.delete("/items/delete", status_code=status.HTTP_200_OK) # Delete Item
def delete_item(jwt: Annotated[str, Security(oauth2_bearer)], id: int = 0, db: Session = Depends(get_db)):
    jwt_user = get_current_user(jwt, db)
    items = db.query(Item).filter(Item.user_id == jwt_user["id"]).all()

    if id >= len(items):
        raise HTTPException(status_code=404, detail=f"Item index {id} out of bounds for length {len(items)}.")

    db_item = items[id]

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")


    
    db.delete(db_item)
    db.commit()


'''
  _    _  _____ ______ _____   _____ 
 | |  | |/ ____|  ____|  __ \ / ____|
 | |  | | (___ | |__  | |__) | (___  
 | |  | |\___ \|  __| |  _  / \___ \ 
 | |__| |____) | |____| | \ \ ____) |
  \____/|_____/|______|_|  \_\_____/ 
                                     
                                     
'''


@router.post("/register")
def create_user(create_user: CreateUserRequest, db: Session = Depends(get_db)):

    email_taken = db.query(User).filter(User.email == create_user.email).first()

    if (email_taken):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User.create(
        username=create_user.username,
        email=create_user.email,
        password=create_user.password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    new_token = create_access_token(
        user_id = user.id,
        token_version = user.token_version,
        expires_delta = timedelta(minutes=20)
    )
    
    return new_token

@router.put("/user/modify") # Modify User Details
def modify_user(user: UpdateUserRequest, jwt: Annotated[str, Security(oauth2_bearer)], db: Session = Depends(get_db)):
    jwt_user = get_current_user(jwt, db)
    db_user = db.query(User).filter(User.id == jwt_user["id"]).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.username = user.username if user.username is not "" and user.username is not None else db_user.username
    db_user.email = user.email if user.email is not "" and user.email is not None  else db_user.email
    if user.password is not "" and user.password is not None :
        db_user.hashed_password = db_user.update_password(user.password)
        if db_user.token_version < 65536:
            db_user.token_version += 1 
        else:
            db_user.token_version = 0

    token = create_access_token(db_user.id, db_user.token_version, timedelta(minutes=20))

    db.commit()
    db.refresh(db_user)

    return token


@router.delete("/user/delete", status_code=status.HTTP_200_OK) # Delete User
def delete_user(jwt: Annotated[str, Security(oauth2_bearer)], db: Session = Depends(get_db)):
    jwt_user = get_current_user(jwt, db)
    db_user = db.query(User).filter(User.id == jwt_user["id"]).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    
    db.delete(db_user)
    db.commit()
