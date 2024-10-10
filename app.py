import streamlit as st
from PIL import Image
import math
from collections import Counter
from utils import similarity_search_via_image, create_search_index_in_azure_ai_search
from azure_blob_storage import create_container_if_not_exists, parse_blob_url, list_blob_sas_urls_from_folder
from gpt_gen import generate_top_n_search_results
from authentication import login, logout
from helpers import clickable_image, handle_action, header_html
from image_data import images, mapped_data
from vars import BLOB_CONNECTION_STRING, CONTAINER_NAME

# Extract the storage account name from the connection string
storage_account_name = BLOB_CONNECTION_STRING.split(";")[1].split("=")[1]
create_search_index_in_azure_ai_search()
container_client = create_container_if_not_exists(
    connection_string= BLOB_CONNECTION_STRING, container_name = CONTAINER_NAME)


# Streamlit app
st.set_page_config(layout="wide") # st.set_page_config(layout="centered")
st.write('')
st.markdown(header_html, unsafe_allow_html=True)


if 'login_status' not in st.session_state:
    st.session_state['login_status'] = False

if st.session_state['login_status']:

    st.title('Find Variants')
    with st.spinner("Wait....Checking/loading all the resources.."):
        if not container_client.exists():
            # If the container doesn't exist, create it
            container_client.create_container()
            print(f"Container {CONTAINER_NAME}")


    if 'selected_image_path' not in st.session_state:
        st.session_state.selected_image_path = None


    selected_image_path = st.session_state.selected_image_path

    # Main Streamlit app
    query_params = st.query_params
    action = query_params.get("action", None)


    # If an action is present in the query parameters, show only the clicked image and the corresponding action output
    if action:
        handle_action(action)
    else:
        st.header("Select an Image")
        for i in range(0, len(images), 3):
            cols = st.columns(3)  # Create 3 columns in a row
            # Process 3 images at a time
            for idx, image_path in enumerate(images[i:i+3]):
                with cols[idx]:  # Access the corresponding column
                    clickable_image(images[idx+i]["path"], f"?action={images[idx+i]['action_name']}")
                    st.write(" ")
    
    # Logout button
    if st.button("Logout"):
        logout()
else:
    login()