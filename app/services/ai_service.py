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
    You are a professional blog writer.

    Generate EXACTLY {count} blog articles about: {prompt}

    Rules:
    - Include an engaging title
    - Write a short introduction
    - Use clear headings and subheadings
    - Explain the topic in simple language
    - Include a conclusion
    - Keep the blog informative and well-structured
    - Return only the blog content
    """

    elif mode == "email":
        return f"""
        You are a professional email writer.

    Generate EXACTLY {count} professional emails based on: {prompt}

    Rules:
    - Include a subject line
    - Include greeting
    - Include email body
    - Include professional closing
    - Use realistic content
    - Avoid placeholders such as [Your Name], [Manager Name], [Date]
    - If information is missing, use generic values naturally
    - Return only the email content
    - End the email with "Best Regards" only
    """

    elif mode in ["linkedin", "linkedin_post"]:
        return f"""
    You are a professional LinkedIn post generator.

    Generate EXACTLY {count} LinkedIn posts about: {prompt}

    Rules:
    - Return only LinkedIn posts
    - No explanation
    - No headings
    - No blog/article format
    - Each post must start with a strong hook
    - Use simple and professional language
    - Maximum 120 words per post
    - Add 3 to 5 relevant hashtags at the end of each post
    - Separate each post using exactly this separator: ###POST###
    - Do not use numbering
    - Do not use bullet points
    """

    return prompt


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

                if line:
                    captions.append(line)

            result = captions[:count]

        elif mode in ["linkedin"]:
            posts = [
                post.strip()
                for post in text.split("###POST###")
                if post.strip()
            ]
            result = posts[:count]

        elif mode == "email":
            emails = [
                email.strip()
                for email in text.split("###EMAIL###")
                if email.strip()
            ]
            result = emails[:count]

        elif mode == "blog":
            blogs = [
                blog.strip()
                for blog in text.split("###BLOG###")
                if blog.strip()
            ]
            result = blogs[:count]

        else:
            result = text
        redis_client.set(key, json.dumps(result), ex=3600)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="AI generation failed"
        )

    
            

        


    
        