import streamlit as st
import os
import uuid
import random
import requests
import time

def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Microsoft", on_click=st.login)

def generate_chat_id():
    # Combine a UUID with a random number for uniqueness
    random_part = random.randint(1000, 9999)
    unique_id = uuid.uuid4().hex[:8]  # Shortened UUID
    chat_id = f"chat_{unique_id}_{random_part}"
    return chat_id

def response_generator(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

def chat_screen():
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
            n8n_response = requests.post(
                os.getenv('N8N_CHAT_WEBHOOK_URL'), json=payload, headers=headers
            )
            if n8n_response.status_code == 200:
                resp_txt = n8n_response.json()["output"].replace("$", "\$")
            else:
                resp_txt = f"Error: {n8n_response.status_code} - {n8n_response.text}"

            response = st.write_stream(response_generator(resp_txt))
        st.session_state.messages.append({"role": "assistant", "content": response})

if not st.user.is_logged_in:
    login_screen()
else:
    chat_screen()
