
import streamlit as st
import openai
import os

st.set_page_config(page_title="Superchat", layout="wide")
st.title("🤖 Superchat")

openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.warning("Please set your OpenAI API key in the environment or Streamlit secrets.")
    st.stop()

# Sidebar input for OpenAI key (if not using Streamlit secrets)
if "OPENAI_API_KEY" not in st.secrets:
    api_key_input = st.sidebar.text_input("🔑 Enter OpenAI API Key", type="password")
    if api_key_input:
        openai.api_key = api_key_input

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
prompt = st.chat_input("Say something to Superchat...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=st.session_state.messages
                )
                msg = response.choices[0].message["content"]
                st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            except Exception as e:
                st.error(f"Error: {e}")
