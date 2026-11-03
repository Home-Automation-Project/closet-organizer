from fastapi import APIRouter, HTTPException

from app.data_loader import DataLoader

router = APIRouter(prefix="/family", tags=["family"])


@router.get("")
async def list_members():
    """Get all family members."""
    return DataLoader.get_family_members()


@router.post("", status_code=201)
async def create_member(data: dict):
    """Create a family member (not implemented - data is static JSON)."""
    raise HTTPException(501, "Creating family members not implemented - data is static JSON")


@router.get("/{member_id}")
async def get_member(member_id: str):
    """Get a single family member."""
    member = DataLoader.get_family_member(member_id)
    if not member:
        raise HTTPException(404, "Member not found")
    return member


@router.put("/{member_id}")
async def update_member(member_id: str, data: dict):
    """Update a family member (not implemented - data is static JSON)."""
    raise HTTPException(501, "Updating family members not implemented - data is static JSON")


@router.delete("/{member_id}", status_code=204)
async def delete_member(member_id: str):
    """Delete a family member (not implemented - data is static JSON)."""
    raise HTTPException(501, "Deleting family members not implemented - data is static JSON")
