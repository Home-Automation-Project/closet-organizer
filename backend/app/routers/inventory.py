from fastapi import APIRouter, HTTPException

from app.services.gsheets_service import GoogleSheetsAdapter

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/basket/{basket_id}")
async def get_basket_inventory(basket_id: str):
    """Get inventory items for a basket from Google Sheets."""
    inventory = GoogleSheetsAdapter.get_inventory(basket_id)
    return {
        "basket_id": basket_id,
        "inventory": inventory
    }


@router.put("/basket/{basket_id}/item/{item_name}", status_code=200)
async def upsert_item(
    basket_id: str,
    item_name: str,
    data: dict,
):
    """Update or create an inventory item in Google Sheets."""
    result = GoogleSheetsAdapter.update_inventory_item(
        basket_id,
        item_name,
        data.get("quantity", 0),
        data.get("expiration_date"),
        data.get("notes")
    )
    return result


@router.delete("/item/{item_id}", status_code=204)
async def delete_inventory_item(item_id: str):
    """Delete an inventory item (not implemented)."""
    raise HTTPException(501, "Deleting inventory not implemented")


@router.get("/scan/{qr_token}")
async def scan_basket(qr_token: str):
    """Scan a basket QR code to access inventory."""
    return {"qr_token": qr_token, "message": "QR scan not implemented"}


@router.get("/basket/{basket_id}/qr.png")
async def get_basket_qr_url(basket_id: str):
    """Get QR code PNG for a basket (not implemented)."""
    raise HTTPException(501, "QR code generation not implemented")

