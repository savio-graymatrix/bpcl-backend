from fastapi import APIRouter, HTTPException, Response, Query, Depends
from typing import List
from bpcl.db.data_models import Bid, CreateBid, UpdateBid
from bpcl.db.utils import (
    CursorPaginationRequest,
    CursorPaginationResponse,
    parse_operator_filter,
)
from typing import Optional
from datetime import datetime, timezone
from beanie.operators import Set


router = APIRouter(prefix="/bids", tags=["Bids"])


# Create Bid
# @router.post("/", response_model=Bid)
@router.post("/")
async def create_bid(bid: CreateBid):
    bid = Bid(**bid.model_dump())
    await bid.insert()
    return bid


# Get All Bids
# @router.get("/", response_model=CursorPaginationResponse[Bid])
@router.get("/")
async def get_all_bids(
    pagination: CursorPaginationRequest = Depends(),
    gstin_no: Optional[str] = Query(None),
    pan_id: Optional[str] = Query(None),
    created_at: Optional[str] = Query(None)
):
    query = {}

    if gstin_no:
        query["gstin_no"] = gstin_no
    if pan_id:
        query["pan_id"] = pan_id
    query.update(parse_operator_filter("created_at", created_at))

    sort_field = pagination.sort_by or "created_at"
    sort_order = pagination.sort_order or -1

    cursor = Bid.find(query).sort((sort_field, sort_order))

    if pagination.after_id:
        after_bid = await Bid.get(pagination.after_id)
        if after_bid:
            after_value = getattr(after_bid, sort_field)
            query[sort_field] = {"$lt" if sort_order == -1 else "$gt": after_value}
            cursor = Bid.find(query).sort((sort_field, sort_order))

    items = await cursor.limit(pagination.limit).to_list()

    next_cursor = items[-1].id if len(items) == pagination.limit else None

    return CursorPaginationResponse[Bid](items=items, next_cursor=next_cursor)


# Get Bid by ID
# @router.get("/{bid_id}", response_model=Bid)
@router.get("/{bid_id}")
async def get_bid(bid_id: str):
    bid = await Bid.get(bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    return bid


# Update Bid
# @router.put("/{bid_id}", response_model=Bid)
@router.put("/{bid_id}")
async def update_bid(bid_id: str, data: Bid):
    bid = await Bid.get(bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bid, field, value)

    bid.updated_at = datetime.now(timezone.utc)
    await bid.save()
    return bid


# Delete Bid
@router.delete("/{bid_id}")
async def delete_bid(bid_id: str):
    bid = await Bid.get(bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    await bid.delete()
    return {"detail": "Bid deleted"}

# Patch Bid
@router.patch("/{bid_id}")
async def patch_bid(bid_id: str, data: UpdateBid):
    bid = await Bid.get(bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    bid.updated_at = datetime.now(timezone.utc)
    await bid.update(
        Set({getattr(Bid, f): v for f, v in data.model_dump(exclude_unset=True).items()})
    )
    # update_data = data.model_dump(exclude_unset=True)
    # for field, value in update_data.items():
    #     setattr(bid, field, value)
    # bid.save()
    return bid