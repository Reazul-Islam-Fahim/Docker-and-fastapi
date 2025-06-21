from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.reply.reply import Reply
from schemas.reply.reply import ReplySchema

async def create_reply(db: AsyncSession, reply: ReplySchema):
    try:
        db_reply = Reply(
            user_id=reply.user_id,
            product_id=reply.product_id,
            review_id=reply.review_id,
            comment=reply.comment,
            is_active=reply.is_active
        )
        db.add(db_reply)
        await db.commit()
        await db.refresh(db_reply)
        return db_reply
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error creating reply: {e}")
        return None

async def get_reply_by_reply_id(db: AsyncSession, reply_id: int):
    try:
        result = await db.execute(select(Reply).filter(Reply.id == reply_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        print(f"Error fetching reply by ID: {e}")
        return None

async def get_replies_by_review_id(db: AsyncSession, review_id: int):
    try:
        result = await db.execute(select(Reply).filter(Reply.review_id == review_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        print(f"Error fetching replies by review ID: {e}")
        return []

async def get_all_replies(db: AsyncSession, skip: int = 0, limit: int = 100):
    try:
        result = await db.execute(select(Reply).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        print(f"Error fetching all replies: {e}")
        return []

async def update_reply(db: AsyncSession, reply_id: int, updated_data: ReplySchema):
    try:
        result = await db.execute(select(Reply).filter(Reply.id == reply_id))
        db_reply = result.scalars().first()
        if not db_reply:
            return None

        if updated_data.comment is not None:
            db_reply.comment = updated_data.comment
        if updated_data.is_active is not None:
            db_reply.is_active = updated_data.is_active

        await db.commit()
        await db.refresh(db_reply)
        return db_reply
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Error updating reply: {e}")
        return None
