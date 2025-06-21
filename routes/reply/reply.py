from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from schemas.reply.reply import ReplySchema
from crud.reply import reply as crud_reply

router = APIRouter(
    prefix="/replies",
    tags=["Replies"]
)

@router.post("")
async def create_reply(reply: ReplySchema, db: AsyncSession = Depends(get_db)):
    db_reply = await crud_reply.create_reply(db, reply)
    if not db_reply:
        raise HTTPException(status_code=400, detail="Failed to create reply")
    return db_reply

@router.get("")
async def get_all_replies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud_reply.get_all_replies(db, skip=skip, limit=limit)

@router.get("/{reply_id}")
async def get_reply_by_id(reply_id: int, db: AsyncSession = Depends(get_db)):
    db_reply = await crud_reply.get_reply_by_reply_id(db, reply_id)
    if not db_reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    return db_reply

@router.get("/review/{review_id}")
async def get_replies_by_review_id(review_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_reply.get_replies_by_review_id(db, review_id)

@router.put("/{reply_id}")
async def update_reply(reply_id: int, updated_reply: ReplySchema, db: AsyncSession = Depends(get_db)):
    db_reply = await crud_reply.update_reply(db, reply_id, updated_reply)
    if not db_reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    return db_reply
