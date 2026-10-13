from database import SessionFactory
import asyncio
from sqlalchemy import select
from datetime import datetime, timezone
from models import User, Skill


async def create_user(id, level = None):
    async with SessionFactory() as session:
        user = await session.get(User, id)
        if user is None:
            user = User(id = id, level = level)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        
        

async def create_skill(user_id, text):
    async with SessionFactory() as session:
        skill = Skill(user_id = user_id, text = text)
        session.add(skill)
        await session.commit()
        await session.refresh(skill)
        

async def update_last_activity(user_id):
    async with SessionFactory() as session:
        user = await session.get(User, user_id)
        user.last_activity = datetime.now(timezone.utc)
        await session.commit()
        
    
async def update_level(user_id, level):
    async with SessionFactory() as session:
        user = await session.get(User, user_id)
        user.level = level
        await session.commit()
        

async def get_level(user_id):
    async with SessionFactory() as session:
        level = await session.execute(select(User.level).where(User.id == user_id))
        return level.scalar_one_or_none()
    

async def get_last_activity(user_id):
    async with SessionFactory() as session:
        last_time = await session.execute(select(User.last_activity).where(User.id == user_id))
        return last_time.scalar_one_or_none()
    

async def get_user_skills(user_id):
    async with SessionFactory() as session:
        result = await session.execute(select(Skill.text).where(Skill.user_id==user_id).order_by(Skill.get_at.desc()))
        return result.scalars().all()
    

async def get_user_info(user_id):
    level = await get_level(user_id)
    last_actiity = await get_last_activity(user_id)
    skills = await get_user_skills(user_id)
    return level, last_actiity, skills