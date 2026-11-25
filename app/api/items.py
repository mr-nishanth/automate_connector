"""Item CRUD-style routes under /api/v1/items."""

from fastapi import APIRouter, HTTPException, status

from app import store
from app.schemas import Item, ItemCreate

router = APIRouter(prefix="/api/v1/items", tags=["items"])


@router.get("", response_model=list[Item])
def list_items() -> list[Item]:
    return store.list_items()


@router.get(
    "/{item_id}",
    response_model=Item,
    responses={404: {"description": "Item not found"}},
)
def get_item(item_id: int) -> Item:
    item = store.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    return store.create_item(payload)
