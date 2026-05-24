# 1. Imports and API setup
from groq import Groq
import base64

client = Groq(
    api_key="sua chave",
)

llava_model = 'llava-v1.5-7b-4096-preview'
llama31_model = 'llama-3.1-70b-versatile'

# 2. Image encoding
image_path = 'images.jpg'
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

base64_image = encode_image(image_path)

# 3. Image to text function
def image_to_text(client, model, base64_image, prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model=model
    )

    return chat_completion.choices[0].message.content

prompt = "Describe this image"
print(image_to_text(client, llava_model, base64_image, prompt))

# 4. Short story generation function
def game_generation(client, image_description):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "What safe game do you suggest and explain in the form of a step-by-step recipe that uses the object described in this image? Note: Write in Portuguese",
            },
            {
                "role": "user",
                "content": image_description,
            }
        ],
        model=llama31_model
    )
    
    return chat_completion.choices[0].message.content

# 5. Single image processing
prompt = '''
Describe this image in detail, including the appearance of the object(s).
'''
image_description = image_to_text(client, llava_model, base64_image, prompt)

print("\n--- Image Description ---")
print(image_description)

print("\n--- Brincadeira ---")
print(game_generation(client, image_description))

