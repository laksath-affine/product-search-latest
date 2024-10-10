from PIL import Image
import base64
import io
import streamlit as st
import math
from azure_blob_storage import parse_blob_url, list_blob_sas_urls_from_folder
from vars import BLOB_CONNECTION_STRING
from gpt_gen import generate_top_n_search_results
from utils import similarity_search_via_image
from image_data import mapped_data, images
from collections import Counter


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
        
def handle_action(action_name):
    clicked_image = next(img for img in images if img["action_name"] == action_name)

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
    
    for image in images:
        if action_name == image["action_name"]:
            on_click(image["path"])


header_html = """
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
"""