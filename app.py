import streamlit as st
from utils import create_search_index_in_azure_ai_search
from azure_blob_storage import create_container_if_not_exists
from authentication import login, logout
from helpers import handle_action, header_html
from image_data import images
from vars import BLOB_CONNECTION_STRING, CONTAINER_NAME
import psutil

# Initialize the Azure search index and container client
def initialize_resources():
    try:
        create_search_index_in_azure_ai_search()
        container_client = create_container_if_not_exists(
            connection_string=BLOB_CONNECTION_STRING,
            container_name=CONTAINER_NAME
        )
        return container_client
    except Exception as e:
        st.error(f"Error initializing resources: {e}")
        return None

# Initialize session state variables
def initialize_session_state():
    if 'login_status' not in st.session_state:
        st.session_state['login_status'] = False
    if 'selected_image_path' not in st.session_state:
        st.session_state['selected_image_path'] = None
    if 'current_action' not in st.session_state:
        st.session_state['current_action'] = None

# Define callback functions
def select_image(action_name):
    st.session_state['current_action'] = action_name

def go_back():
    st.session_state['current_action'] = None

def main():
    # Set up the page configuration and header
    memory = psutil.virtual_memory()
    st.write(f"Memory Usage: {memory.percent}%")

    st.set_page_config(layout="wide")
    st.write('')
    st.write('')
    st.markdown(header_html, unsafe_allow_html=True)

    initialize_session_state()

    if st.session_state['login_status']:
        st.title('Find Variants')

        # Initialize resources
        with st.spinner("Wait... Checking/loading all the resources..."):
            container_client = initialize_resources()
            if container_client is None:
                st.stop()
            if not container_client.exists():
                container_client.create_container()

        # Main application logic
        action = st.session_state['current_action']

        if action:
            # Handle the selected action
            handle_action(action)
            st.button("Back", on_click=go_back)
        else:
            # Display images for selection
            st.header("Select an Image")
            num_columns = 3  # Number of images per row
            image_rows = [images[i:i + num_columns] for i in range(0, len(images), num_columns)]
            for row in image_rows:
                cols = st.columns(num_columns)
                for idx, image_data in enumerate(row):
                    with cols[idx]:
                        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                        st.image(image_data["path"], width=250)
                        st.button("Select", key=f"select_{image_data['action_name']}",
                                  on_click=select_image, args=(image_data['action_name'],))
                        st.markdown("</div>", unsafe_allow_html=True)
        # Logout button
        if st.button("Logout"):
            logout()
    else:
        # Display login screen
        login()

if __name__ == "__main__":
    main()
