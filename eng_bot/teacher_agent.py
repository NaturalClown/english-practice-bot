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
            "You are a language instructor helping a user improve "
            "their language skills through conversational practice.",
            """Return your answer in exactly this format:

            <SKILL>
            A short lesson title, no longer than 255 characters, This section should focus solely on the lesson topic; there is no need to write anything about the matters mentioned by the user.This section should focus solely on the lesson topic; there is no need to write anything about the matters mentioned by the user.;
            </SKILL>
            <LESSON>
            The complete lesson text, including the title as its first line.
            </LESSON>

            Do not add anything before, between, or after these two blocks.
            Do not use these marker strings anywhere else in your response.""",
            "The lesson title must also be the first line of text, "
            "exactly as it appears in skill.",
            "",
            "Follow this lesson structure:",
            "1. Lesson title.",
            "2. A brief, natural reply to the user's message, "
            "addressing its topic.",
            "3. Analysis of the user's most significant language errors. "
            "Point out no more than two errors. If there are many, "
            "prioritize the most important ones.",
            "4. A short lesson explaining one important language point. "
            "Include the correct usage and a few examples.",
            "5. Two short exercises for practice.",
            "",
            "If the user has made mistakes, base the lesson on one "
            "of the most important mistakes.",
            "Do not invent errors. Distinguish actual mistakes from "
            "acceptable informal or conversational language.",
            "",
            "Use plain text suitable for Telegram. Avoid Markdown "
            "headings, excessive asterisks, hashtags, and decorative "
            "formatting. Keep the response concise and easy to read."
        ]

        if level is not None:
            prompt.extend([
                "",
                f"Estimated proficiency level: {level}.",
                "Adapt the explanation, examples, exercises, and "
                "vocabulary to this level.",
                "If the user has made no significant errors, choose "
                "a grammar topic appropriate for this level at random.",
                "Avoid topics already covered, using the existing "
                "skills list if provided.",
                "At the end of the lesson, provide 5-10 useful words "
                "or phrases appropriate for this level, with meanings "
                "and/or translations. Do not omit this vocabulary section."
            ])

        if skills:
            prompt.extend([
                "",
                "Previously covered skills and lesson topics:",
                *[f"- {skill}" for skill in skills],
                "Avoid repeating these topics. Choose a different "
                "topic unless reviewing one is genuinely necessary."
            ])

        return "\n".join(prompt)

    async def get_answer(self, text, skills=None, level=None):
        skill, lesson_text = None, None      
        for model in models:

            try:
                system_prompt = await self.get_prompt(skills=skills, level=level)
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": f"{text}"
                        }
                    ],
                    temperature=0.3,
                    max_tokens=5000, 
                
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
                    return None, "Couldn't parse the lesson"

                skill = match.group(1).strip()
                lesson_text = match.group(2).strip()

                if not skill or not lesson_text:
                    print("Invalid skill or lesson")
                    return None, "Couldn't parse the lesson"
            
                if len(skill)>255:
                    skill = skill[:255]

                return model, skill, lesson_text
          
            except Exception as e:
                print(f"Error with model {model}, trying next")
                    
        else: 
            return None, None, "Couldn't get answer"

