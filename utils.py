import json
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ExhaustiveKnnAlgorithmConfiguration, ExhaustiveKnnParameters,
    SearchIndex, SearchField, SearchFieldDataType, SearchableField, SearchIndex,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField, SemanticSearch, VectorSearch,
    HnswAlgorithmConfiguration, HnswParameters, VectorSearchAlgorithmKind, VectorSearchProfile, VectorSearchAlgorithmMetric
)
from azure.search.documents.models import QueryAnswerType, QueryCaptionType, QueryType, VectorizedQuery
from azure_embeddings import vectorize_image_with_filepath
from vars import AZURE_SEARCH_SERVICE_ENDPOINT, AZURE_SEARCH_INDEX_NAME, AZURE_SEARCH_INDEX_KEY, \
    VISION_ENDPOINT, VISION_VERSION, VISION_SUBSCRIPTION_KEY
azure_search_credential = AzureKeyCredential(AZURE_SEARCH_INDEX_KEY)


# Create an SDK client
admin_client = SearchIndexClient(endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, index_name=AZURE_SEARCH_INDEX_NAME, credential=azure_search_credential)
search_client = SearchClient(endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, index_name=AZURE_SEARCH_INDEX_NAME, credential=azure_search_credential)


def create_search_index_in_azure_ai_search():
    fields = [
        SearchableField(name="index_number", type=SearchFieldDataType.String, key=True,
                        searchable=True, filterable=True, retrievable=True),
        SearchableField(name="category", type=SearchFieldDataType.String,
                        searchable=True, filterable=True, retrievable=True),
        SearchableField(name="brand", type=SearchFieldDataType.String,
                        searchable=True, filterable=True, retrievable=True),
        SearchableField(name="flavour", type=SearchFieldDataType.String,
                        searchable=True, filterable=True, retrievable=True),
        SearchableField(name="quantity", type=SearchFieldDataType.String,
                        searchable=True, filterable=True, retrievable=True),
        SearchableField(name="product_folder_link", type=SearchFieldDataType.String,
                        searchable=True, filterable=True, retrievable=True),
        SearchableField(name="product_description", type=SearchFieldDataType.String,
                        searchable=True, filterable=True, retrievable=True),
        SearchField(name="product_description_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, retrievable=True, vector_search_dimensions=1024, vector_search_profile_name="myHnswProfile")
    ]

    # Configure the vector search configuration
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=400,
                    ef_search=500,
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            ),
            ExhaustiveKnnAlgorithmConfiguration(
                name="myExhaustiveKnn",
                kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                parameters=ExhaustiveKnnParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE
                )
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            ),
            VectorSearchProfile(
                name="myExhaustiveKnnProfile",
                algorithm_configuration_name="myExhaustiveKnn",
            )
        ]
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="product_folder_link"),
            content_fields=[SemanticField(field_name="product_description")]
        )
    )

    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=AZURE_SEARCH_INDEX_NAME, fields=fields,
                        vector_search=vector_search, semantic_search=semantic_search)
    result = admin_client.create_or_update_index(index)
    print(f' {result.name} created')


def similarity_search_via_image(file_path, category, brand):

    image_embedding = vectorize_image_with_filepath(file_path, VISION_ENDPOINT, VISION_SUBSCRIPTION_KEY, VISION_VERSION)
    image_vector_query = VectorizedQuery(
        vector=image_embedding, k_nearest_neighbors=100, fields="product_description_vector")

    text_results = search_client.search(
        vector_queries=[image_vector_query],
        select=["product_folder_link",
                "product_description",
                "category",
                "brand",
                "flavour",
                "quantity"],
        filter=f"category eq '{category}' and brand eq '{brand}'",
        query_type=QueryType.SEMANTIC, semantic_configuration_name='my-semantic-config', query_caption=QueryCaptionType.EXTRACTIVE, query_answer=QueryAnswerType.EXTRACTIVE,
        top=100
    )

    return list(text_results)


def get_images_and_json(folder_path):
    image_list = []
    json_list = []

    # Walk through the folder and subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file is an image (you can add more extensions if needed)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_list.append(os.path.join(root, file))

            # Check if the file is a JSON file
            if file.lower().endswith('.json'):
                json_file_path = os.path.join(root, file)
                # Load the JSON content
                with open(json_file_path, 'r') as f:
                    json_content = json.load(f)
                    # Extracting the nested dictionary without using the key
                    extracted_data = next(iter(json_content.values()))[0]

                    # Changing keys to lowercase
                    modified_data = {key.lower(): value for key,
                                     value in extracted_data.items()}
                    json_list.append(modified_data)

    return image_list, json_list
