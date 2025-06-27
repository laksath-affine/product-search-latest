import requests
from gpt_gen import generate_item_description
from vars import VISION_ENDPOINT, VISION_SUBSCRIPTION_KEY, VISION_VERSION
import pathlib

def vectorize_image_with_filepath(
        image_filepath: str,
        endpoint: str,
        key: str,
        api_version: str = "2024-02-01",
        model_version: str = "2023-04-15",
):
    """
    Returns the embedding vector of a local image using Azure AI Vision
    Multimodal Embeddings (GA).

    Parameters
    ----------
    image_filepath : str  Path to local image
    endpoint       : str  e.g. 'https://myvision.cognitiveservices.azure.com/'
    key            : str  subscription key
    api_version    : str  default '2024-02-01'
    model_version  : str  '2023-04-15' (multilingual) or '2022-04-11'
    """
    with open(image_filepath, "rb") as img:
        data = img.read()

    # Ensure single trailing slash
    endpoint = endpoint.rstrip("/") + "/"

    url = (
        f"{endpoint}retrieval:vectorizeImage"
        f"?api-version={api_version}&model-version={model_version}"
    )

    headers = {
        "Content-Type": "application/octet-stream",
        "Ocp-Apim-Subscription-Key": key,
    }
    
    image_path = pathlib.Path(image_filepath)
    resp = requests.post(url, data=image_path.read_bytes(), headers=headers, timeout=30)
    if resp.ok:
        return resp.json()["vector"]

    raise RuntimeError(f"{resp.status_code}: {resp.text}")



def vectorize_image_with_url(
    image_url: str,
    endpoint: str,
    key: str,
    version: str,
):
    """
    Generates a vector embedding for a remote image using Azure AI Vision 4.0
    (Vectorize Image API).

    :param image_url: The URL of the image.
    :param endpoint: The endpoint of the Azure AI Vision resource.
    :param key: The access key of the Azure AI Vision resource.
    :param version: The version of the API.
    :return: The vector embedding of the image.
    """
    # Vectorize Image API
    version = f'?api-version={version}&modelVersion=latest'
    vision_api = endpoint + "retrieval:vectorizeImage" + version

    headers = {
        "Content-type": "application/json",
        "Ocp-Apim-Subscription-Key": key,
    }

    try:
        r = requests.post(vision_api, json={"url": image_url}, headers=headers)
        if r.status_code == 200:
            image_vector = r.json()["vector"]
            return image_vector
        else:
            print(
                f"An error occurred while processing {image_url}. "
                f"Error code: {r.status_code}."
            )
    except Exception as e:
        print(f"An error occurred while processing {image_url}: {e}")

    return None


def vectorize_text(
    text: str,
    endpoint: str,
    key: str,
    version: str,
):
    """
    Generates a vector embedding for a text prompt using Azure AI Vision 4.0
    (Vectorize Text API).

    :param text: The text prompt.
    :param endpoint: The endpoint of the Azure AI Vision resource.
    :param key: The access key of the Azure AI Vision resource.
    :param version: The version of the API.
    :return: The vector embedding of the image.
    """
    # Vectorize Text API
    version = f'?api-version={version}&modelVersion=latest'
    vision_api = endpoint + "retrieval:vectorizeText" + version

    headers = {
        "Content-type": "application/json",
        "Ocp-Apim-Subscription-Key": key
    }

    try:
        r = requests.post(vision_api, json={"text": text}, headers=headers)
        if r.status_code == 200:
            text_vector = r.json()["vector"]
            return text_vector
        else:
            print(
                f"An error occurred while processing the prompt '{text}'. "
                f"Error code: {r.status_code}."
            )
    except Exception as e:
        print(f"An error occurred while processing the prompt '{text}': {e}")

    return None


def vectorize_image_with_gpt(folder_path=None, image_paths=None, b64s=None):
    description = generate_item_description(
        folder_path=folder_path, image_paths=image_paths, b64s=b64s)

    return {
        'embedding': vectorize_text(description, VISION_ENDPOINT, VISION_SUBSCRIPTION_KEY, VISION_VERSION),
        'description': description
    }
