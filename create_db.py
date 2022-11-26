import asyncio
import sqlalchemy.ext.asyncio
import db.name
import db.schema


async def _async_main():
    print('creating db')

    engine = sqlalchemy.ext.asyncio.create_async_engine(
        f'sqlite+aiosqlite:///{db.name.DB_FILENAME}'
    )

    async with engine.begin() as conn:
        await conn.run_sync(db.schema.Base.metadata.drop_all)
        await conn.run_sync(db.schema.Base.metadata.create_all)

    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(_async_main())
