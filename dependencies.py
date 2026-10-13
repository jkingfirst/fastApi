from models import AsyncSessionFactory
async def get_session():
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()