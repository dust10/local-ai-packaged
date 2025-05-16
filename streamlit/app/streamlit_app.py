import streamlit as st
import os
import uuid
import random
import requests
import time
import logging
import sys
import json

PARAM_EMBEDDED = "embedded"

logger = logging.getLogger("streamlit_app")
if not logger.hasHandlers():
    # Create a new handler if no handlers are present
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Microsoft", on_click=st.login)

def generate_chat_id():
    # Combine a UUID with a random number for uniqueness
    random_part = random.randint(1000, 9999)
    unique_id = uuid.uuid4().hex[:8]  # Shortened UUID
    chat_id = f"chat_{unique_id}_{random_part}"
    logger.debug(f"Generated chat ID: {chat_id}")
    return chat_id

def response_generator(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

def chat_screen():
    if not st.session_state.embedded:
        st.title("iShift HR Assistant")

        st.markdown(
            """
            <style>
                div[data-testid="stColumn"]:nth-of-type(2)
                {
                    text-align: end;
                } 
            </style>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Welcome, {st.user.name}!")
        with col2:
            st.button("Log out", on_click=st.logout, key="logout_button")
    
    if "chat_id" not in st.session_state:
        st.session_state["chat_id"] = generate_chat_id()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Invoke N8N workflow
            headers = {
                "Authorization": f"Bearer {os.getenv('N8N_CHAT_BEARER_TOKEN')}",
                "Content-Type": "application/json",
            }
            payload = {
                "sessionId": f"{st.session_state.chat_id}",
                "chatInput": prompt
            }
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            with st.status("Generating response...", expanded=True) as status:
                n8n_response = requests.post(
                    os.getenv('N8N_CHAT_WEBHOOK_URL'), json=payload, headers=headers
                )
                logger.debug(f"N8N response: {n8n_response.status_code} - {n8n_response.text}")
                if n8n_response.status_code == 200:
                    resp_txt = n8n_response.json()["output"].replace("$", "\$")
                else:
                    resp_txt = f"Error: {n8n_response.status_code} - {n8n_response.text}"
                status.update(label="Complete", state="complete", expanded=False)

            response = st.write_stream(response_generator(resp_txt))
        st.session_state.messages.append({"role": "assistant", "content": response})

logger.debug(f"Query params: {st.query_params}")

if "embedded" not in st.session_state:
    if PARAM_EMBEDDED in st.query_params:
        logger.debug(f"Embed parameter found: {st.query_params[PARAM_EMBEDDED]}")
        st.session_state.embedded = st.query_params[PARAM_EMBEDDED].lower() == "true"
    else:
        logger.debug("Embed parameter not found, defaulting to False")
        st.session_state.embedded = False

st.set_page_config(
    page_title="iShift HR Assistant",
    page_icon=":robot:",
    layout= "wide" if st.session_state.embedded else "centered"
)

if not st.user.is_logged_in:
    login_screen()
else:
    logger.debug(f"User is logged in: {st.user.name}")
    chat_screen()
