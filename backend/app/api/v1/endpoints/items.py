from fastapi import APIRouter, HTTPException, status
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter()

_items_db: list[dict] = [
    {"id": 1, "title": "First Sample Item", "description": "Welcome to FastAPI"},
    {"id": 2, "title": "Second Sample Item", "description": "Connected to Next.js"},
]


@router.get("", response_model=list[ItemResponse], summary="List Items")
def list_items() -> list[dict]:
    return _items_db


@router.get("/{item_id}", response_model=ItemResponse, summary="Get Item by ID")
def get_item(item_id: int) -> dict:
    for item in _items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with id {item_id} not found",
    )


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Item",
)
def create_item(payload: ItemCreate) -> dict:
    new_id = len(_items_db) + 1
    new_item = {
        "id": new_id,
        "title": payload.title,
        "description": payload.description,
    }
    _items_db.append(new_item)
    return new_item
