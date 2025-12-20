import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import base64

# 1) Load .env from the same directory as this file
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)

# 2) Read the key explicitly
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    # Fail fast with a clear message
    raise RuntimeError(f"OPENAI_API_KEY not found in .env at: {ENV_PATH}")

# 3) Create the OpenAI client with the key
client = OpenAI(api_key=api_key)


def generate_recipe_image_payload(recipe_data: dict, dynamic_data: dict) -> str:
    vessel = dynamic_data.get('vessel', 'an artisanal ceramic plate')
    visual_desc = dynamic_data.get('visual_desc', 'richly colored, textured food, elegantly plated')
    garnishes = dynamic_data.get('garnishes', 'fresh herbs, scattered spices')
    ingredients_prop = dynamic_data.get('ingredients_prop', 'folds of steam, a few scattered ingredients')

    FIXED_AESTHETIC = "High-resolution editorial food photograph, rustic artisanal style, warm and textural."
    FIXED_SURFACE = "A textured dark stone surface."
    FIXED_LIGHTING = "Illuminated with a soft side-light setup to create depth and emphasize the dish’s warm hues and subtle sheen, no harsh shadows."
    FIXED_COMPOSITION = "Captured at a shallow 35–45° angle to highlight the presentation. Razor-sharp focus on the center of the dish, with a gentle falloff around the edges. 3:2 aspect ratio."
    
    final_prompt = (
        f"{FIXED_AESTHETIC} "
        f"{recipe_data['name']}, featuring {visual_desc}, is {vessel}, placed on {FIXED_SURFACE}. "
        f"Garnished with {garnishes}. "
        f"The scene includes {ingredients_prop}. "
        f"{FIXED_LIGHTING} {FIXED_COMPOSITION}"
    )
    
    return final_prompt
    


def generate_image_url(prompt: str) -> str:
    """
    Calls OpenAI to generate an image URL using the final prompt.
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        n=1,
        response_format="url",
    )

    return response.data[0].url
