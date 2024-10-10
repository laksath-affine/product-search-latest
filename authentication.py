import streamlit as st
from vars import USERNAME, PASSWORD

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state['login_status'] = True
            st.success("Logged in successfully")
            st.rerun()
        else:
            st.error("Incorrect username or password")

def logout():
    st.session_state['login_status'] = False
    st.rerun()
