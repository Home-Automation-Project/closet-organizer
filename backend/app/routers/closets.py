from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.crud import crud
from app.schemas.schemas import (
    ClosetCreate, ClosetDetailOut, ClosetOut, ClosetUpdate,
    ShelfCreate, ShelfOut, ShelfUpdate,
    BasketCreate, BasketOut, BasketUpdate, BasketWithStatus,
)
from app.models.models import BasketStatus

router = APIRouter(prefix="/closets", tags=["closets"])


# ---------------------------------------------------------------------------
# Closets
# ---------------------------------------------------------------------------

@router.get("", response_model=List[ClosetOut])
async def list_closets(db: AsyncSession = Depends(get_db)):
    return await crud.get_closets(db)


@router.post("", response_model=ClosetOut, status_code=201)
async def create_closet(data: ClosetCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_closet(db, data)


@router.get("/{closet_id}", response_model=ClosetDetailOut)
async def get_closet(closet_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_closet(db, closet_id)
    if not obj:
        raise HTTPException(404, "Closet not found")
    # Attach status to each basket
    shelves_out = []
    for shelf in obj.shelves:
        baskets_out = []
        for basket in shelf.baskets:
            inv = await crud.get_inventory(db, basket.id)
            status = crud.compute_basket_status(inv)
            b = BasketWithStatus.model_validate(basket)
            b.status = status
            baskets_out.append(b)
        shelf_dict = ShelfOut.model_validate(shelf).model_dump()
        shelf_dict["baskets"] = baskets_out
        shelves_out.append(shelf_dict)
    closet_dict = ClosetOut.model_validate(obj).model_dump()
    closet_dict["shelves"] = shelves_out
    return closet_dict


@router.put("/{closet_id}", response_model=ClosetOut)
async def update_closet(closet_id: int, data: ClosetUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud.update_closet(db, closet_id, data)
    if not obj:
        raise HTTPException(404, "Closet not found")
    return obj


@router.delete("/{closet_id}", status_code=204)
async def delete_closet(closet_id: int, db: AsyncSession = Depends(get_db)):
    if not await crud.delete_closet(db, closet_id):
        raise HTTPException(404, "Closet not found")


# ---------------------------------------------------------------------------
# Shelves
# ---------------------------------------------------------------------------

shelves_router = APIRouter(prefix="/shelves", tags=["shelves"])


@shelves_router.get("", response_model=List[ShelfOut])
async def list_shelves(closet_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_shelves(db, closet_id)


@shelves_router.post("", response_model=ShelfOut, status_code=201)
async def create_shelf(data: ShelfCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_shelf(db, data)


@shelves_router.get("/{shelf_id}", response_model=ShelfOut)
async def get_shelf(shelf_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_shelf(db, shelf_id)
    if not obj:
        raise HTTPException(404, "Shelf not found")
    return obj


@shelves_router.put("/{shelf_id}", response_model=ShelfOut)
async def update_shelf(shelf_id: int, data: ShelfUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud.update_shelf(db, shelf_id, data)
    if not obj:
        raise HTTPException(404, "Shelf not found")
    return obj


@shelves_router.delete("/{shelf_id}", status_code=204)
async def delete_shelf(shelf_id: int, db: AsyncSession = Depends(get_db)):
    if not await crud.delete_shelf(db, shelf_id):
        raise HTTPException(404, "Shelf not found")


# ---------------------------------------------------------------------------
# Baskets
# ---------------------------------------------------------------------------

baskets_router = APIRouter(prefix="/baskets", tags=["baskets"])


@baskets_router.get("", response_model=List[BasketOut])
async def list_baskets(shelf_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_baskets(db, shelf_id)


@baskets_router.post("", response_model=BasketOut, status_code=201)
async def create_basket(data: BasketCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_basket(db, data)


@baskets_router.get("/{basket_id}", response_model=BasketOut)
async def get_basket(basket_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_basket(db, basket_id)
    if not obj:
        raise HTTPException(404, "Basket not found")
    return obj


@baskets_router.put("/{basket_id}", response_model=BasketOut)
async def update_basket(basket_id: int, data: BasketUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud.update_basket(db, basket_id, data)
    if not obj:
        raise HTTPException(404, "Basket not found")
    return obj


@baskets_router.delete("/{basket_id}", status_code=204)
async def delete_basket(basket_id: int, db: AsyncSession = Depends(get_db)):
    if not await crud.delete_basket(db, basket_id):
        raise HTTPException(404, "Basket not found")
