import google.generativeai as genai
import os
from dotenv import load_dotenv
from app.utils.redis_client import redis_client
from app.utils.cache_key import generate_cache_key
import json
from fastapi import HTTPException

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

def build_prompt(prompt: str, mode: str, count: int = 1):

    if mode == "caption":
        return f"""
You are an Instagram caption generator.

Generate EXACTLY {count} Instagram captions about: {prompt}

Rules:
- Only captions
- No explanation
- No headings
- No categories
- No tips
- No numbering
- Each caption must be on a new line
- Maximum 10 words per caption
"""

    elif mode == "blog":
        return f"""
Write a detailed blog post about: {prompt}
"""

    elif mode == "email":
        return f"""
Write a professional email about: {prompt}
"""

    elif mode == "linkedin":
        return f"""
Write a professional LinkedIn post about: {prompt}
"""

    return prompt

# def generate_content(prompt: str, count: int = 1):
#     final_prompt = f"""
#     You are an AI content assistant.

#     Generate {count} Instagram captions.

#     Topic:
#     {prompt}

#     Rules:
#     - Each caption in new line
#     - No numbering
#     - No explanation
#     """
#     response = model.generate_content(final_prompt)
#     text = response.text.strip()

#     captions = [line.strip("- ").strip() for line in text.split("\n") if line.strip()]
#     return captions[:count]

def generate_content(prompt: str, mode: str, count: int = 1):
    try:
        key = generate_cache_key(prompt + mode + str(count))
        try:
            cached = redis_client.get(key)
        except Exception:
            cached = None

        if cached:
            return json.loads(cached)

        final_prompt = build_prompt(prompt, mode, count)

        response = model.generate_content(final_prompt)

        text = response.text.strip()

        if mode == "caption":

            lines = text.split("\n")

            captions = []
            for line in lines:
                line = line.strip("- ").strip()

                if (
                    line
                    and "caption" not in line.lower()
                    and "tip" not in line.lower()
                    and "pro" not in line.lower()
                    and len(line) < 120
                ):
                    captions.append(line)
            result = captions[:count]
        else:
            result = text
        redis_client.set(key, json.dumps(result), ex=3600)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="AI generation failed"
        )

    
            

        


    
        