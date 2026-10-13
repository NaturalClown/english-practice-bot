import asyncio
from groq import AsyncGroq
import os
from dotenv import load_dotenv
load_dotenv()


class VoiceToText():
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv('GROQ_API'))
        
    async def recognize(self, audio):
        result = await self.client.audio.transcriptions.create(
            file=("voice.ogg", audio), 
            model="whisper-large-v3-turbo", 
            response_format="text",
            language='en'
            )        
        return result




