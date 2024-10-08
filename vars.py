import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

# AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
# AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME')
# AZURE_SEARCH_INDEX_KEY = os.getenv('AZURE_SEARCH_INDEX_KEY')

# VISION_ENDPOINT = os.getenv('VISION_ENDPOINT') + 'computervision/'
# VISION_SUBSCRIPTION_KEY = os.getenv('VISION_SUBSCRIPTION_KEY')
# VISION_VERSION = os.getenv('VISION_VERSION')

# AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
# AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
# AZURE_OPENAI_AI_VERSION = os.getenv('AZURE_OPENAI_AI_VERSION')
# AZURE_OPENAI_NAME = os.getenv('AZURE_OPENAI_NAME')

# BLOB_CONNECTION_STRING = os.getenv('BLOB_CONNECTION_STRING')
# CONTAINER_NAME = os.getenv('CONTAINER_NAME')

AZURE_SEARCH_SERVICE_ENDPOINT = st.secrets["AZURE_SEARCH_SERVICE_ENDPOINT"]
AZURE_SEARCH_INDEX_NAME = st.secrets["AZURE_SEARCH_INDEX_NAME"]
AZURE_SEARCH_INDEX_KEY = st.secrets["AZURE_SEARCH_INDEX_KEY"]

VISION_ENDPOINT = st.secrets["VISION_ENDPOINT"] + 'computervision/'
VISION_SUBSCRIPTION_KEY = st.secrets["VISION_SUBSCRIPTION_KEY"]
VISION_VERSION = st.secrets["VISION_VERSION"]

AZURE_OPENAI_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_API_KEY = st.secrets["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_AI_VERSION = st.secrets["AZURE_OPENAI_AI_VERSION"]
AZURE_OPENAI_NAME = st.secrets["AZURE_OPENAI_NAME"]

BLOB_CONNECTION_STRING = st.secrets["BLOB_CONNECTION_STRING"]
CONTAINER_NAME = st.secrets["CONTAINER_NAME"]

USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]