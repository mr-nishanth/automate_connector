"""Simple in-memory item repository."""

from app.schemas import Item, ItemCreate

_items: dict[int, Item] = {}
_next_id: int = 1


def reset_store() -> None:
    """Reset the store to its seeded state."""
    global _next_id
    _items.clear()
    _next_id = 1
    for payload in (
        ItemCreate(name="Widget", description="A small widget", price=9.99),
        ItemCreate(name="Gadget", description="A useful gadget", price=19.5),
        ItemCreate(name="Gizmo", description=None, price=4.25),
    ):
        create_item(payload)


def list_items() -> list[Item]:
    return list(_items.values())


def get_item(item_id: int) -> Item | None:
    return _items.get(item_id)


def create_item(payload: ItemCreate) -> Item:
    global _next_id
    item = Item(id=_next_id, **payload.model_dump())
    _items[item.id] = item
    _next_id += 1
    return item


reset_store()
