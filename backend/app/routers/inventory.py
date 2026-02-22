from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
import io

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.crud import crud
from app.schemas.schemas import (
    InventoryItemCreate, InventoryItemUpdate,
    InventoryItemOut, InventoryItemWithStatus,
    BasketDetailOut, BasketWithStatus,
)
from app.services import qr_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/basket/{basket_id}", response_model=BasketDetailOut)
async def get_basket_inventory(basket_id: int, db: AsyncSession = Depends(get_db)):
    basket = await crud.get_basket(db, basket_id)
    if not basket:
        raise HTTPException(404, "Basket not found")
    inv = basket.inventory
    status = crud.compute_basket_status(inv)
    items_with_status = []
    for item in inv:
        item_out = InventoryItemWithStatus.model_validate(item)
        item_out.quantity_status = crud.compute_quantity_status(
            item.quantity, item.item_definition.recommended_qty
        )
        item_out.expiration_status = crud.compute_expiration_status(item.expiration_date)
        items_with_status.append(item_out)
    basket_out = BasketWithStatus.model_validate(basket)
    basket_out.status = status
    result = BasketDetailOut.model_validate(basket_out)
    result.inventory = items_with_status
    return result


@router.put("/basket/{basket_id}/item/{item_definition_id}", response_model=InventoryItemWithStatus)
async def upsert_item(
    basket_id: int,
    item_definition_id: int,
    data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    item = await crud.upsert_inventory_item(db, basket_id, item_definition_id, data)
    out = InventoryItemWithStatus.model_validate(item)
    out.quantity_status = crud.compute_quantity_status(
        item.quantity, item.item_definition.recommended_qty
    )
    out.expiration_status = crud.compute_expiration_status(item.expiration_date)
    return out


@router.delete("/item/{inventory_id}", status_code=204)
async def delete_inventory_item(inventory_id: int, db: AsyncSession = Depends(get_db)):
    if not await crud.delete_inventory_item(db, inventory_id):
        raise HTTPException(404, "Inventory item not found")


@router.get("/basket/{basket_id}/qr.png")
async def basket_qr_png(basket_id: int, db: AsyncSession = Depends(get_db)):
    basket = await crud.get_basket(db, basket_id)
    if not basket:
        raise HTTPException(404, "Basket not found")
    png = qr_service.generate_basket_qr_png(basket.qr_token)
    return Response(content=png, media_type="image/png")


@router.get("/scan/{qr_token}", response_model=BasketDetailOut)
async def scan_basket(qr_token: str, db: AsyncSession = Depends(get_db)):
    basket = await crud.get_basket_by_qr(db, qr_token)
    if not basket:
        raise HTTPException(404, "Basket not found")
    inv = basket.inventory
    status = crud.compute_basket_status(inv)
    items_with_status = []
    for item in inv:
        item_out = InventoryItemWithStatus.model_validate(item)
        item_out.quantity_status = crud.compute_quantity_status(
            item.quantity, item.item_definition.recommended_qty
        )
        item_out.expiration_status = crud.compute_expiration_status(item.expiration_date)
        items_with_status.append(item_out)
    basket_out = BasketWithStatus.model_validate(basket)
    basket_out.status = status
    result = BasketDetailOut.model_validate(basket_out)
    result.inventory = items_with_status
    return result
