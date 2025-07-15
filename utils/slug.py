import re
from unidecode import unidecode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text


async def generate_unique_slug(
    db: AsyncSession,
    name: str,
    model,
    slug_field: str = "slug"
):
    slug = unidecode(name.lower())
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    slug = re.sub(r'[-]+', '-', slug)

    counter = 1
    original_slug = slug

    while True:
        column = getattr(model, slug_field)
        result = await db.execute(select(model).where(column == slug))
        if not result.scalar_one_or_none():
            return slug
        slug = f"{original_slug}-{counter}"
        counter += 1
