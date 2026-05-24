import requests
import base64
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import chainlit as cl

# Function to resize image if larger than a given size
def resize_image(image_path, max_size=(800, 800)):
    image = Image.open(image_path)
    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
        image.thumbnail(max_size, Image.LANCZOS)
        resized_path = "resized_" + os.path.basename(image_path)
        image.save(resized_path)
        return resized_path
    return image_path

# Function to invoke NVIDIA API and get bounding boxes
def get_bounding_boxes(image_path, api_key, message_content):
    invoke_url = "https://ai.api.nvidia.com/v1/vlm/microsoft/kosmos-2"

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    assert len(image_b64) < 180_000, \
        "To upload larger images, use the assets API (see docs)"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": f'{message_content} <img src="data:image/png;base64,{image_b64}" />'
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.20,
        "top_p": 0.20
    }

    response = requests.post(invoke_url, headers=headers, json=payload)
    response_data = response.json()

    bboxes = []
    response_text = ""
    if 'choices' in response_data:
        response_text = response_data['choices'][0]['message']['content']
        entities = response_data['choices'][0]['message']['entities']
        for entity in entities:
            bboxes.extend(entity['bboxes'])

    return bboxes, response_text

# Function to plot image with bounding boxes
def plot_image_with_bboxes(image_path, bboxes):
    image = Image.open(image_path)
    fig, ax = plt.subplots(1)
    ax.imshow(image)

    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'cyan']

    for bbox, color in zip(bboxes, colors):
        x = bbox[0] * image.width
        y = bbox[1] * image.height
        width = (bbox[2] - bbox[0]) * image.width
        height = (bbox[3] - bbox[1]) * image.height
        rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor=color, facecolor='none')
        ax.add_patch(rect)

    plt.axis('off')
    return fig

# Chainlit message handler to process uploaded images
@cl.on_message
async def on_message(msg: cl.Message):
    if not msg.elements:
        await cl.Message(content="No file attached").send()
        return

    # Process images exclusively
    images = [file for file in msg.elements if "image" in file.mime]

    if not images:
        await cl.Message(content="No image file attached").send()
        return

    image_path = images[0].path
    resized_image_path = resize_image(image_path)
    api_key = "colocar sua chave aqui"

    bboxes, response_text = get_bounding_boxes(resized_image_path, api_key, msg.content)
    fig = plot_image_with_bboxes(resized_image_path, bboxes)

    elements = [
        cl.Pyplot(name="plot", figure=fig, display="inline"),
    ]
    await cl.Message(
        content=f"{response_text}",
        elements=elements,
    ).send()
