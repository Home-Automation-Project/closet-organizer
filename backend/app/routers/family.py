from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.crud import crud
from app.schemas.schemas import FamilyMemberCreate, FamilyMemberOut, FamilyMemberUpdate

router = APIRouter(prefix="/family", tags=["family"])


@router.get("", response_model=List[FamilyMemberOut])
async def list_members(db: AsyncSession = Depends(get_db)):
    return await crud.get_family_members(db)


@router.post("", response_model=FamilyMemberOut, status_code=201)
async def create_member(data: FamilyMemberCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_family_member(db, data)


@router.get("/{member_id}", response_model=FamilyMemberOut)
async def get_member(member_id: int, db: AsyncSession = Depends(get_db)):
    obj = await crud.get_family_member(db, member_id)
    if not obj:
        raise HTTPException(404, "Member not found")
    return obj


@router.put("/{member_id}", response_model=FamilyMemberOut)
async def update_member(member_id: int, data: FamilyMemberUpdate, db: AsyncSession = Depends(get_db)):
    obj = await crud.update_family_member(db, member_id, data)
    if not obj:
        raise HTTPException(404, "Member not found")
    return obj


@router.delete("/{member_id}", status_code=204)
async def delete_member(member_id: int, db: AsyncSession = Depends(get_db)):
    if not await crud.delete_family_member(db, member_id):
        raise HTTPException(404, "Member not found")
