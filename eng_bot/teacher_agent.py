import asyncio
from openai import AsyncOpenAI
import re
import os

models = [
    "inclusionai/ling-3.1-flash",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "dots-studio/dots-3-note-preview:free",
    'thinkingmachines/inkling-small:free',
    "apodex/apodex-1.1-mini:free",
    "nvidia/nemotron-3.5-lightning:free", 
    "nvidia/nemotron-3.5-content-safety:free", 
    ]

class TeacherAgent():
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENROUTER_API'), base_url="https://openrouter.ai/api/v1")
    
    async def get_prompt(self, skills=None, level=None):
        prompt = [
            "You are a friendly English tutor. Prioritize natural, "
            "engaging conversation and respond meaningfully to what "
            "the user says. Ask follow-up questions when appropriate.",
            "",
            "Return exactly this format:",
            "<SKILL>",
            "A short lesson topic (max 255 characters).",
            "</SKILL>",
            "<LESSON>",
            "Your complete response, starting with the lesson topic.",
            "</LESSON>",
            "",
            "Do not write anything outside these blocks or use their "
            "markers elsewhere.",
            "",
            "Guidelines:",
            "- Focus primarily on the user's message and keep the "
            "conversation going.",
            "- Correct up to two significant English mistakes, "
            "briefly explaining the corrections. Do not invent errors "
            "or criticize acceptable informal language.",
            "- End with a short, relevant grammar lesson, preferably "
            "based on a mistake the user made. If there are no "
            "significant errors, choose an appropriate new topic.",
            "- Include a few examples and two brief exercises.",
            "- Keep everything concise and adapt it to the user's level.",
            "- Use plain text suitable for Telegram. Avoid excessive "
            "formatting and vocabulary lists."
        ]

        if level is not None:
            prompt.extend([
                "",
                f"User's English level: {level}.",
                "Adapt your language and explanations accordingly."
            ])

        if skills:
            prompt.extend([
                "",
                "Previously covered topics:",
                *[f"- {skill}" for skill in skills],
                "Avoid repeating them unless necessary."
            ])

        return "\n".join(prompt)

    async def get_answer(self, text, skills=None, level=None, story=None):
        skill, lesson_text = None, None      
        for model in models:

            try:
                system_prompt = await self.get_prompt(skills=skills, level=level)
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt
                    }
                ]

                for msg in story:
                    messages.append({
                        "role": "assistant" if msg.author else "user",
                        "content": msg.content
                    })

                messages.append({
                    "role": "user",
                    "content": text
                })

                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2500, 
                
                    #response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content or ""

                match = re.search(
                    r"<SKILL>\s*(.*?)\s*</SKILL>\s*"
                    r"<LESSON>\s*(.*?)\s*</LESSON>",
                    content,
                    re.DOTALL
                )

                if not match:
                    print(f"Invalid model response: {content!r}")
                    return None, None, "Couldn't parse the lesson"

                skill = match.group(1).strip()
                lesson_text = match.group(2).strip()

                if not skill or not lesson_text:
                    print("Invalid skill or lesson")
                    return None, None, "Couldn't parse the lesson"
            
                if len(skill)>255:
                    skill = skill[:255]

                return model, skill, lesson_text
          
            except Exception as e:
                print(f"Error with model {model}, trying next ({e})")
                    
        else: 
            return None, None, "Couldn't get answer"

