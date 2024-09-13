import base64
import io
import streamlit as st
import os
from PIL import Image
import math
from collections import Counter
from utils import similarity_search_via_image, create_search_index_in_azure_ai_search
from azure_blob_storage import create_container_if_not_exists, parse_blob_url, list_blob_sas_urls_from_folder
from gpt_gen import generate_top_n_search_results
from vars import BLOB_CONNECTION_STRING, CONTAINER_NAME

# Extract the storage account name from the connection string
storage_account_name = BLOB_CONNECTION_STRING.split(";")[1].split("=")[1]
create_search_index_in_azure_ai_search()
container_client = create_container_if_not_exists(
    connection_string= BLOB_CONNECTION_STRING, container_name = CONTAINER_NAME)


# Streamlit app
st.set_page_config(layout="wide") # st.set_page_config(layout="centered")
st.markdown("""
    <div style='text-align: center; margin-top:-70px; margin-bottom: 5px;margin-left: -10px;'>
    <h2 style='font-size: 40px; font-family: Courier New, monospace;
                    letter-spacing: 2px; text-decoration: none;'>
    <img src="https://acis.affineanalytics.co.in/assets/images/logo_small.png" alt="logo" width="70" height="60">
    <span style='background: linear-gradient(45deg, #ed4965, #c05aaf);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            text-shadow: none;'>
                    AFFINE
    </span>
    <span style='font-size: 40%;'>

    </span>
    </h2>
    </div>
    """, unsafe_allow_html=True)


st.title('Find Variants')
with st.spinner("Wait....Checking/loading all the resources.."):
    if not container_client.exists():
        # If the container doesn't exist, create it
        container_client.create_container()
        print(f"Container {CONTAINER_NAME}")

images = [
    {
        'path': 'images/Del Monte Fresh Cut Corn Cream Style Golden Sweet - 14.75 Oz/Del Monte Fresh Cut Corn Cream Style Golden Sweet - 14.75 Oz_1.jpeg',
        'action_name': 'action_name1',
        'metadata': {'category': 'canned products', 'brand': 'del monte', 'flavour': 'Cut Corn Cream Style Golden Sweet', 'quantity': '14.5'}
    },
    {
        'path': 'images/Halo Top Chocolate chip cookie dough ice cream/Halo Top Chocolate chip cookie dough ice cream_1.png',
        'action_name': 'action_name2',
        'metadata': {'category': 'Frozen Foods', 'brand': 'halo top', 'flavour': 'Chocolate chip cookie dough', 'quantity': '16'}
    },
    {
        'path': 'images/So Delicious Vanilla Bean/So Delicious Vanilla Bean_1.png',
        'action_name': 'action_name3',
        'metadata': {'category': 'Frozen Foods', 'brand': 'so delicious', 'flavour': 'Vanilla', 'quantity': '16'}
    },
    {
        'path': 'images/Pepsi Soda Cola - 20 Fl. Oz/Pepsi Soda Cola - 20 Fl. Oz._1.jpeg',
        'action_name': 'action_name4',
        'metadata': {'category': 'Beverages', 'brand': 'pepsi', 'flavour': 'Soda Cola', 'quantity': '20'}
    },
    {
        'path': 'images/Coca-Cola Soda Pop Classic - 12-12 Fl. Oz/Coca-Cola Soda Pop Classic - 12-12 Fl. Oz_1.jpeg',
        'action_name': 'action_name5',
        'metadata': {'category': 'Beverages', 'brand': 'coca-cola', 'flavour': 'Soda Pop Classic', 'quantity': '144'}
    },
    {
        'path': 'images/Soleil Water Sparkling Blood Orange 24-12 Fz - 24-12 FZ/Soleil Water Sparkling Blood Orange 24-12 Fz - 24-12 FZ_1.jpeg',
        'action_name': 'action_name6',
        'metadata': {'category': 'Beverages', 'brand': 'soleil', 'flavour': 'Sparkling Blood Orange', 'quantity': '24'}
    },
    {
        'path': 'images/Zapps 2.625 Oz S&V Chip - 2.62 Oz/Zapps 2.625 Oz S&V Chip - 2.62 Oz.jpg',
        'action_name': 'action_name7',
        'metadata': {'category': 'Cookies, Snacks & Candy', 'brand': 'lays', 'flavour': 'Sea Salt', 'quantity': '2.62'}
    },
    {
        'path': 'images/Lays Dip French Onion - 15 Oz/Lays Dip French Onion - 15 Oz_1.jpeg',
        'action_name': 'action_name8',
        'metadata': {'category': 'Cookies, Snacks & Candy', 'brand': 'lays', 'flavour': 'Dip Fresh onion', 'quantity': '15'}
    },
    {
        'path': 'images/Lays Kettle Cooked All Dressed 8oz - 8 OZ/Lays Kettle Cooked All Dressed 8oz - 8 OZ_1.jpg',
        'action_name': 'action_name9',
        'metadata': {'category': 'Cookies, Snacks & Candy', 'brand': 'lays', 'flavour': 'Kettle Cooked All Dressed', 'quantity': '8'}
    },
    # {
    #     'path': 'images/Lays Cheetos Potato Chips Cheese Flavored - 2.625 OZ/Lays Cheetos Potato Chips Cheese Flavored - 2.625 OZ_1.jpg',
    #     'action_name': 'action_name10',
    #     'metadata': {'category': 'Cookies, Snacks & Candy', 'brand': 'lays', 'flavour': 'Cheese', 'quantity': '2.625'}
    # },
    # {
    #     'path': 'images/Juanitas Foods Mexican Gourmet Sauce Nacho Cheese Can - 15 Oz/Juanitas Foods Mexican Gourmet Sauce Nacho Cheese Can - 15 Oz_5.jpeg',
    #     'action_name': 'action_name11',
    #     'metadata': {'category': 'canned products', 'brand': 'juanitas foods', 'flavour': 'Mexican Gourmet Sauce Nacho Cheese', 'quantity': '15'}
    # }
]


mapped_data = {}
for i in range(len(images)):
    mapped_data[images[i]["path"]] = images[i]['metadata']

if 'selected_image_path' not in st.session_state:
    st.session_state.selected_image_path = None


selected_image_path = st.session_state.selected_image_path


def display_images(relevant_context):
    for k in range(math.ceil(len(relevant_context)/5)):
        columns = st.columns(5)
        j = 0
        for i, context in enumerate(relevant_context[5*k:5*(k+1)]):
            container_name, folder_name = parse_blob_url(
                context['product_folder_link'])
            image_url = list_blob_sas_urls_from_folder(BLOB_CONNECTION_STRING, container_name, folder_name)[0]

            # Display images in the second row
            with columns[j]:
                st.image(image_url, width=150)
                caption = f"""
                **Brand**: {context['brand']}  <br>
                **Flavour**: {context['flavour']}  <br>
                **Quantity**: {context['quantity']} Oz  <br>
                """
                st.markdown(caption, unsafe_allow_html=True)
            j += 1


def on_click(selected_image_path):
    product_info = mapped_data[selected_image_path]
    # print(product_info)
    relevant_context = similarity_search_via_image(selected_image_path, product_info['category'], product_info['brand'])
    # print(relevant_context)
    
    product_description_list = [
        f"Product Description: {result['product_description']}\n\nFlavour: {result['flavour']}\n Quantity: {result['quantity']}" for result in relevant_context
    ]

    # print(product_description_list)

    for i in range(4):
        try:
            second_filter_items = generate_top_n_search_results(product_description_list, selected_image_path)
            integer_list = list(map(lambda x: int(x) - 1, second_filter_items.strip("[]").split(", ")))
            
            repeated_items = {item: count for item, count in Counter(integer_list).items() if count > 1}
            print(second_filter_items, len(integer_list), len(set(integer_list)))
            print(repeated_items)

            # if len(integer_list) == len(set(integer_list)) and len(integer_list) > len(product_description_list)//2-2:
            second_filter_relevant_context = [relevant_context[item_no] for item_no in integer_list]
            
            st.markdown(f"## **{'Output'}**", unsafe_allow_html=True)
            display_images(second_filter_relevant_context)
            break
        except:
            pass
    

def clickable_image(image_path, action_name):

    image = Image.open(image_path)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    # Create a clickable image using HTML
    image_html = f'''
    <a href="{action_name}">
        <img src="data:image/png;base64,{image_base64}" style="width:50%; height:auto;"/>
    </a>
    '''
    st.markdown(image_html, unsafe_allow_html=True)



def handle_action(action_name):
    for image in images:
        if action_name == image["action_name"]:
            on_click(image["path"])


# Main Streamlit app
query_params = st.query_params
action = query_params.get("action", None)


# If an action is present in the query parameters, show only the clicked image and the corresponding action output
if action:
    clicked_image = next(img for img in images if img["action_name"] == action)

    image_path = clicked_image["path"]

    # Display only the clicked image
    image = Image.open(image_path)
    st.image(image, width=300)
    caption = f"""
    **Brand**: {clicked_image["metadata"]["brand"]}  <br>
    **Flavour**: {clicked_image["metadata"]["flavour"]}  <br>
    **Quantity**: {clicked_image["metadata"]["quantity"]} Oz  <br>
    """
    st.markdown(caption, unsafe_allow_html=True)
    # Show the output of the handle_action function
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
