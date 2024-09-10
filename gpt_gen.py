from openai import AzureOpenAI
import os
import base64
import requests
from vars import AZURE_OPENAI_AI_VERSION, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_NAME

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def url_to_base64(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        base64_image = base64.b64encode(response.content).decode('utf-8')
        return base64_image
    else:
        raise Exception(
            f"Failed to retrieve image. Status code: {response.status_code}")


def get_text_api_result(prompt, base64_images=None):
    completion_client = AzureOpenAI(
        azure_endpoint = AZURE_OPENAI_ENDPOINT,
        api_key = AZURE_OPENAI_API_KEY,
        api_version = AZURE_OPENAI_AI_VERSION
    )

    if base64_images:
        attachments = [{"type": "text", "text": prompt}]
        for base64_image in base64_images:
            attachments.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            )
        completion = completion_client.chat.completions.create(
            model = AZURE_OPENAI_NAME,
            messages=[
                {
                    "role": "user",
                    "content": attachments
                }
            ]
        )
    else:
        completion = completion_client.chat.completions.create(
            model = AZURE_OPENAI_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    return completion.choices[0].message.content


tagging_prompt = """Analyze the provided images meticulously and extract detailed information based on the following categories:
    Extract all text from the image, ensuring no details are missed. Pay special attention to any certifications, health claims, brand names, and nutritional information. 
    Carefully include text from all sections, including the top, center, bottom, and sides of the packaging. 
    Review the image thoroughly to capture any additional small text or logos that 
    might be important, such as certifications or endorsements (e.g., American Heart Association, Gluten Free).
    Provide the extracted text in a clear, organized format

"""
prompt = "Create a detailed product description with the information from these images. Ensure the text is unformatted, without any bold, italic, or other special formatting."


def generate_item_description(folder_path=None, b64s=None, image_paths=None):
    # prompt = "Analyze the provided set of images and generate a structured and detailed description that includes only the product's nutritional values, ingredients, serving sizes, packaging claims, allergen information, and other relevant details. Do not include any additional commentary, concluding statements, or extraneous text beyond the factual information presented in the images. Ensure the text is unformatted, without any bold, italic, or other special formatting."
    prompt = "Create a detailed product description with the information from these images. Ensure the text is unformatted, without any bold, italic, or other special formatting."

    if not b64s:
        # files = [f"{folder_path}/{file}" for file in os.listdir(folder_path)]
        files = [f"{folder_path}/{file}" for file in os.listdir(
            folder_path) if not file.lower().endswith('.json')]
        if image_paths is not None:
            files = image_paths
        b64s = [encode_image(file) for file in files]

    return get_text_api_result(prompt, b64s)


def generate_filtered_search_results(items, instruction):
    item_list = ''
    for i, item in enumerate(items, start=1):
        item_list += f'ITEM {i}: {item.strip()}\n\n'
    prompt = (
        f"You are a highly skilled food suggestion expert. Based on the items provided and the user's request: '{instruction}', "
        "identify and return only the relevant item numbers. The output should strictly follow this format: [item_number1, item_number2, ...]. "
        "For example, if the relevant items are Item No 1, Item No 3, Item No 6, Item No 12, and Item No 22, the output should be [1, 3, 6, 12, 22]. "
        "Do not include any additional information or text.\nItems:\n"
        f"{item_list}"
    )
    return get_text_api_result(prompt)


def generate_top_10_search_results(items, flavour, quantity):
    item_list = ''
    for i, item in enumerate(items, start=1):
        item_list += f'ITEM {i}: {item.strip()}\n\n'
    count = len(items)
    prompt = (
        f"You are a highly skilled food suggestion expert. From the given input's metadata: Flavour: {flavour} ; Quantity: {quantity} Oz,"
        f"Idenify and return the top {count} ranked (best to worst) most relevant item numbers. The output should strictly follow this format: [item_number1, item_number2, ...]. "
        f"If there are fewer than {count} relevant items, return as many as are available in the correct format but try to return {count} unless you find results to be completely irrelevant. "
        f"Give the first preference to the similar looking flavour followed by the quantity."
        f"Even if you find some exact matches, then you can still look for other items that could potentially be similar based on the description of the item."
        f"For example, if the relevant items are Item No 1, Item No 3, Item No 6, Item No 12, and Item No 22, the output should be [1, 3, 6, 12, 22]. "
        f"Do not include any additional information or text.\nItems:\n"
        f"{item_list}"
    )

    return get_text_api_result(prompt)


def generate_top_10_search_results1(items, product_flavour_list, product_quantity_list, selected_image_flavour, selected_image_quantity):
    item_list = ''
    # Iterate over the three lists simultaneously and get the index with enumerate
    for i, (item, flavour, quantity) in enumerate(zip(items, product_flavour_list, product_quantity_list)):
        # for i, item in enumerate(items, start=1):
        item_list += f'ITEM {i}: (flavour:{flavour},quantity:{quantity}) {item.strip()}\n\n'

    prompt = (
        f"You are a highly skilled food suggestion expert."
        "Based on the below given selected_image_flavour and selected_image_quantity sort and return the top 10 most relevant item numbers. The output should strictly follow this format: [item_number1, item_number2, ...]. "
        "If there are fewer than 10 relevant items, return as many as are available in the correct format. "
        "For example, if the relevant items are Item No 1, Item No 3, Item No 6, Item No 12, and Item No 22, the output should be [1, 3, 6, 12, 22]. "
        "Do not include any additional information or text.\nItems:\n"
        f"selected_image_flavour: {selected_image_flavour}"
        f"selected_image_quantity: {selected_image_quantity}"
        f"{item_list}"
    )

    return get_text_api_result(prompt)
