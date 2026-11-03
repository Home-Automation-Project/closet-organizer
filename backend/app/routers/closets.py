from typing import List, Optional
from fastapi import APIRouter, HTTPException

from app.data_loader import DataLoader

router = APIRouter(prefix="/closets", tags=["closets"])


# ---------------------------------------------------------------------------
# Closets
# ---------------------------------------------------------------------------

@router.get("")
async def list_closets():
    """Get all closets with their shelves and baskets."""
    closets = DataLoader.get_closets()
    return closets


@router.post("", status_code=201)
async def create_closet(data: dict):
    """Create a new closet (not implemented - data is static JSON)."""
    raise HTTPException(501, "Creating closets not implemented - data is static JSON")


@router.get("/{closet_id}")
async def get_closet(closet_id: str):
    """Get a single closet with its structure."""
    closet = DataLoader.get_closet(closet_id)
    if not closet:
        raise HTTPException(404, "Closet not found")
    return closet


@router.put("/{closet_id}")
async def update_closet(closet_id: str, data: dict):
    """Update a closet (not implemented - data is static JSON)."""
    raise HTTPException(501, "Updating closets not implemented - data is static JSON")


@router.delete("/{closet_id}", status_code=204)
async def delete_closet(closet_id: str):
    """Delete a closet (not implemented - data is static JSON)."""
    raise HTTPException(501, "Deleting closets not implemented - data is static JSON")


# Shelves router - simplified for static data
shelves_router = APIRouter(prefix="/shelves", tags=["shelves"])


@shelves_router.get("")
async def list_shelves(closet_id: str):
    """Get shelves for a closet."""
    closet = DataLoader.get_closet(closet_id)
    if not closet:
        raise HTTPException(404, "Closet not found")
    return closet.get("shelves", [])


@shelves_router.post("", status_code=201)
async def create_shelf(data: dict):
    """Create a shelf (not implemented - data is static JSON)."""
    raise HTTPException(501, "Creating shelves not implemented - data is static JSON")


@shelves_router.get("/{shelf_id}")
async def get_shelf(shelf_id: str):
    """Get a single shelf (not implemented)."""
    raise HTTPException(501, "Getting individual shelves not implemented")


@shelves_router.put("/{shelf_id}")
async def update_shelf(shelf_id: str, data: dict):
    """Update a shelf (not implemented - data is static JSON)."""
    raise HTTPException(501, "Updating shelves not implemented - data is static JSON")


@shelves_router.delete("/{shelf_id}", status_code=204)
async def delete_shelf(shelf_id: str):
    """Delete a shelf (not implemented - data is static JSON)."""
    raise HTTPException(501, "Deleting shelves not implemented - data is static JSON")


# Baskets router - simplified for static data
baskets_router = APIRouter(prefix="/baskets", tags=["baskets"])


@baskets_router.get("")
async def list_baskets(shelf_id: str):
    """Get baskets for a shelf."""
    shelves = []
    for closet in DataLoader.get_closets():
        shelves.extend(closet.get("shelves", []))
    
    for shelf in shelves:
        if shelf["id"] == shelf_id:
            return shelf.get("baskets", [])
    
    raise HTTPException(404, "Shelf not found")


@baskets_router.post("", status_code=201)
async def create_basket(data: dict):
    """Create a basket (not implemented - data is static JSON)."""
    raise HTTPException(501, "Creating baskets not implemented - data is static JSON")


@baskets_router.get("/{basket_id}")
async def get_basket(basket_id: str):
    """Get a single basket (not implemented)."""
    raise HTTPException(501, "Getting individual baskets not implemented")


@baskets_router.put("/{basket_id}")
async def update_basket(basket_id: str, data: dict):
    """Update a basket (not implemented - data is static JSON)."""
    raise HTTPException(501, "Updating baskets not implemented - data is static JSON")


@baskets_router.delete("/{basket_id}", status_code=204)
async def delete_basket(basket_id: str):
    """Delete a basket (not implemented - data is static JSON)."""
    raise HTTPException(501, "Deleting baskets not implemented - data is static JSON")
