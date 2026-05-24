import base64
import io
from PIL import Image
import ollama

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
    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": "Traduza para o português o que está escrito nessa placa da imagem.",
            "images": [image_base64]
        }]
    )
    return response.get('message', {}).get('content', '').strip()

if __name__ == "__main__":
    image_path = 'examples/cardapio.png'  # Replace with your image path
    base64_image = encode_image_to_base64(image_path)
    ocr_text = get_ocr_output_from_image(base64_image)
    print(ocr_text)