import asyncio
from database import engine
from models import Base, User, Skill

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    await engine.dispose()
    
if __name__ == "__main__":
    asyncio.run(main())
