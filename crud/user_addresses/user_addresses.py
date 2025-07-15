from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user_addresses.user_addresses import UserAddresses
from schemas.user_addresses.user_addresses import UserAddressesSchema


async def create_user_address(db: AsyncSession, address_data: UserAddressesSchema):
    new_address = UserAddresses(
        user_id=address_data.user_id,
        address_line=address_data.address_line,
        city=address_data.city,
        state=address_data.state,
        postal_code=address_data.postal_code,
        country=address_data.country,
        is_default=address_data.is_default
    )
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return new_address


async def get_user_addresses_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(UserAddresses).where(UserAddresses.user_id == user_id)
    )
    return result.scalars().all()


async def get_user_address_by_id(db: AsyncSession, address_id: int):
    result = await db.execute(
        select(UserAddresses).where(UserAddresses.id == address_id)
    )
    return result.scalar_one_or_none()


async def update_user_address(
    db: AsyncSession, address_id: int, updated_data: UserAddressesSchema
) -> UserAddresses | None:
    result = await db.execute(
        select(UserAddresses).where(UserAddresses.id == address_id)
    )
    address = result.scalar_one_or_none()

    if address:
        address.user_id = updated_data.user_id
        address.address_line = updated_data.address_line
        address.city = updated_data.city
        address.state = updated_data.state
        address.postal_code = updated_data.postal_code
        address.country = updated_data.country
        address.is_default = updated_data.is_default

        await db.commit()
        await db.refresh(address)

    return address


async def set_default_address(db: AsyncSession, user_id: int, address_id: int):
    result = await db.execute(
        select(UserAddresses).where(UserAddresses.user_id == user_id)
    )
    addresses = result.scalars().all()
    updated = False
    for addr in addresses:
        if addr.id == address_id:
            if not addr.is_default:
                addr.is_default = True
                updated = True
        elif addr.is_default:
            addr.is_default = False
            updated = True
    if updated:
        await db.commit()
    return updated
