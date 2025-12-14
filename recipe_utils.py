import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import base64

# 1) Load .env from the same directory as this file
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# If your .env is next to main.py instead, use:
# ENV_PATH = BASE_DIR / " . . " / ".env"   # remove spaces in "..", I have to space to avoid formatting

load_dotenv(dotenv_path=ENV_PATH, override=True)

# 2) Read the key explicitly
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    # Fail fast with a clear message
    raise RuntimeError(f"OPENAI_API_KEY not found in .env at: {ENV_PATH}")

# 3) Create the OpenAI client with the key
client = OpenAI(api_key=api_key)


def generate_recipe_image_payload(recipe_data: dict, dynamic_data: dict) -> str:
    """
    Constructs a highly detailed, hyperrealistic image prompt for professional magazine food photography.
    """
    # Defaults are clean and modern for a hyperrealistic magazine aesthetic
    # vessel = dynamic_data.get('vessel', 'pristine white ceramic bowl')
    # visual_desc = dynamic_data.get('visual_desc', 'vibrant food textures, meticulously arranged plating')
    # garnishes = dynamic_data.get('garnishes', 'delicate microgreens, precisely placed edible flowers')
    # ingredients_prop = dynamic_data.get('ingredients_prop', 'a few pristine ingredients strategically positioned')

    # # garnish_text = ", ".join(garnishes.split(', '))
    # # surroundings_text = ", ".join(ingredients_prop.split(', '))

    # # These fixed elements describe a realistic studio setup
    # FIXED_AESTHETIC = "Hyperrealistic commercial food photography, clean editorial style, bright and vibrant with tack-sharp focus, shot for a high-end gourmet magazine cover."
    # FIXED_PROPS = "A single, flawless presentation plate, minimalist stainless steel cutlery, absolute minimal clutter."
    # FIXED_LIGHTING = "Professional studio strobes, bright, even illumination, very high contrast with defined highlights, no harsh shadows."
    # FIXED_BACKGROUND = "A seamless white or light grey matte backdrop, polished marble surface, extremely clean environment."

    # # The final prompt is crafted to sound like a creative brief rather than a list of commands
    # final_prompt = (
    #     f"{FIXED_AESTHETIC} "
    #     f"A {vessel} is the center of the image, placed on a {FIXED_BACKGROUND}. "
    #     f"It is perfectly filled with {recipe_data['name']}, featuring {visual_desc}. "
    #     f"Garnished with {garnish_text}. "
    #     f"The setup includes {surroundings_text} and {FIXED_PROPS}. "
    #     f"{FIXED_LIGHTING} The photo has a shallow depth of field, an award-winning photo, cinematic detail."
    # )
    

    vessel = dynamic_data.get('vessel', 'an artisanal ceramic plate')
    visual_desc = dynamic_data.get('visual_desc', 'richly colored, textured food, elegantly plated')
    garnishes = dynamic_data.get('garnishes', 'fresh herbs, scattered spices')
    ingredients_prop = dynamic_data.get('ingredients_prop', 'folds of steam, a few scattered ingredients')

    # These fixed elements describe a realistic, warm studio setup
    FIXED_AESTHETIC = "High-resolution editorial food photograph, rustic artisanal style, warm and textural."
    FIXED_SURFACE = "A textured dark stone surface."
    FIXED_LIGHTING = "Illuminated with a soft side-light setup to create depth and emphasize the dish’s warm hues and subtle sheen, no harsh shadows."
    FIXED_COMPOSITION = "Captured at a shallow 35–45° angle to highlight the presentation. Razor-sharp focus on the center of the dish, with a gentle falloff around the edges. 3:2 aspect ratio."
    

        # The final prompt is crafted to sound like a creative brief rather than a list of commands
    final_prompt = (
        # f"{FIXED_AESTHETIC} "
        # f"A {vessel} is the center of the image, placed on a {FIXED_BACKGROUND}. "
        # f"It is perfectly filled with {recipe_data['name']}, featuring {visual_desc}. "
        # f"Garnished with {garnish_text}. "
        # f"The setup includes {surroundings_text} and {FIXED_PROPS}. "
        # f"{FIXED_LIGHTING} The photo has a shallow depth of field, an award-winning photo, cinematic detail."
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
