import asyncio
import os
from aiogram import Bot, Dispatcher, html, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
from voice_to_text import VoiceToText
from teacher_agent import TeacherAgent
from crud import *

story_limit = 14
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

dp = Dispatcher()
voice_to_text = VoiceToText()

agent = TeacherAgent()

@dp.message(CommandStart())
async def send_welcome(message):
    await message.reply(f"""Hi, {message.from_user.first_name}!
                        
    Send voice messages to practice English. I'll correct your mistakes and explain grammar.
                        
    To set your level, send a text message containing only A1, A2, B1, B2, C1, or C2.
                        
    I'll suggest grammar topics suited to your level. My memory is limited to the last 14 messages, including my own replies.
                        
    Happy practicing!""")
    await create_user(id=message.from_user.id)


@dp.message(F.voice)
async def get_voice(message, bot):
    voice_message = await bot.download(message.voice)
    result = await voice_to_text.recognize(voice_message)
    await message.reply(f"You said:\n{str(result)}\n\nPreparing a response may take some time.")
    if len(str(result >= 2500)):
        await message.reply("Too long message")
    else:
        user_level = await get_level(message.from_user.id)
        user_skills = await get_user_skills(message.from_user.id)
        story = await get_story(message.from_user.id, story_limit)
        model, skill, answer = await agent.get_answer(result, level = user_level, skills=user_skills, story=story)
        if skill is not None: 
            await create_skill(user_id = message.from_user.id, text = skill)
            await update_last_activity(message.from_user.id)
            await create_message(message.from_user.id, str(result), 0)
            await create_message(message.from_user.id, answer, 1)
        
        await message.reply(answer)


@dp.message(Command("me"))
async def get_info(message):
    level, last_actiity, skills = await get_user_info(message.from_user.id)
    await message.reply(f"Your level is {level}, your last actiity was at {last_actiity} and your skills are {skills}")
    

@dp.message(F.text)
async def get_text(message):
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    print(message.text)
    if message.text in levels: 
        await update_level(user_id = message.from_user.id, level = message.text)
        await message.reply(f"Your level is now set to {message.text}")
    else: 
        await message.reply("Sorry, for now you can only tell me your level of English in text (one of these: A1, A2, B1, B2, C1, C2)")


async def main():
    print("Ready to work!")
    bot = Bot(token = TOKEN)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    asyncio.run(main())