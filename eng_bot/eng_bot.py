import asyncio
import os
from quopri import decodestring
from aiogram import Bot, Dispatcher, html, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
from voice_to_text import VoiceToText
from teacher_agent import TeacherAgent
from crud import *

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

dp = Dispatcher()
voice_to_text = VoiceToText()

agent = TeacherAgent()

@dp.message(CommandStart())
async def send_welcome(message):
    print(message.from_user.id)
    await message.reply(f"Hi, {message.from_user.first_name}! You can state your current English proficiency level (on the A1-C2 scale, write a text message consisting of just two characters) or simply send a voice message. Unfortunately, I can't hold a full conversation just yet, but I will try to point out any errors you make and explain the relevant grammar. Alternatively, if your message contains no errors and you've specified your level, I'll select a short grammar topic or structure to explain to you. Also, if you let me know your level, I'll suggest a few words for you to learn that are appropriate for that level! Happy practicing!")
    await create_user(id=message.from_user.id)
    




@dp.message(F.voice)
async def get_voice(message, bot):
    voice_message = await bot.download(message.voice)
    result = await voice_to_text.recognize(voice_message)
    await message.reply(f"You said:\n{str(result)}\n\nPreparing a response may take some time.")
    print(str(result))
    
    user_level = await get_level(message.from_user.id)
    user_skills = await get_user_skills(message.from_user.id)

    model, skill, answer = await agent.get_answer(result, level = user_level, skills=user_skills)
    print(skill)
    await message.reply(f"The response was prepared by model {model}")
    if skill is not None: 
        await create_skill(user_id = message.from_user.id, text = skill)
        await update_last_activity(message.from_user.id)
    await message.reply(answer)


@dp.message(Command("me"))
async def get_info(message):
    level, last_actiity, skills = await get_user_info(message.from_user.id)
    await message.reply(f"Your level is {level}, your last actiity was at {last_actiity} and your skills are {skills}")
    

@dp.message(F.text)
async def get_text(message):
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'A1+', 'A2+', 'B1+', 'B2+', 'C1+']
    print(message.text)
    if message.text in levels: 
        await update_level(user_id = message.from_user.id, level = message.text)
        await message.reply(f"Your level is now set to {message.text}")
    else: 
        await message.reply("Sorry, for now I can only tell you your level of English in text (Sorry, for now I can only tell you your level of English in text (one of these: A1, A1+, A2, A2+, B1, B1+, B2, B2+, C1, C1+, C2")


async def main():
    print("Ready to work!")
    bot = Bot(token = TOKEN)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    asyncio.run(main())