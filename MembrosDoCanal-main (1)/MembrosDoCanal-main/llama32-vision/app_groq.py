import base64
import io
from PIL import Image

from groq import Groq

client = Groq(api_key="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")


def encode_image_to_base64(image_path: str, format: str = "PNG") -> str:
    
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')


def get_ocr_output_from_image(image_base64: str, model: str = "llama3.2-vision:11b") -> str:
    """Sends an image to the Llama OCR model and returns structured text output.

    Args:
        image_base64 (str): Base64-encoded image string.
        model (str): The model version to use for OCR (default is latest Llama 3.2 Vision).

    Returns:
        str: Extracted and structured text from the image.
    """
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Traduza para o português o que está escrito na imagem."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                    },
                },
            ],
        }
    ],
    model="llama-3.2-90b-vision-preview",
    )

    return chat_completion.choices[0].message.content

   

if __name__ == "__main__":
    image_path = 'examples/cardapio.png'  # Replace with your image path
    base64_image = encode_image_to_base64(image_path)
    ocr_text = get_ocr_output_from_image(base64_image)
    print(ocr_text)