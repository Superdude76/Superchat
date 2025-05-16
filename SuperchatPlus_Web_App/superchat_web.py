
import streamlit as st
import openai
import os
import tempfile
import io
import contextlib

st.set_page_config(page_title="Superchat+", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧠 Superchat+</h1>", unsafe_allow_html=True)

openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.warning("Please set your OpenAI API key in the environment or Streamlit secrets.")
    st.stop()

# Sidebar options
st.sidebar.title("🛠️ Tools & Options")
use_voice = st.sidebar.checkbox("🎤 Enable Text-to-Speech")
file_uploaded = st.sidebar.file_uploader("📂 Upload a File (text, PDF, etc.)")

# Display file contents
if file_uploaded:
    st.subheader("📖 Uploaded File Contents:")
    content = file_uploaded.read().decode("utf-8", errors="ignore")
    st.text_area("File Preview", content, height=200)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Say something to Superchat...")

# Optional: Text-to-Speech using gTTS
def speak(text):
    try:
        from gtts import gTTS
        import base64
        tts = gTTS(text)
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(fp.name)
        audio_bytes = open(fp.name, "rb").read()
        b64 = base64.b64encode(audio_bytes).decode()
        md = f"""
        <audio controls autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Voice error: {e}")

# Run Python code safely
def run_code_block(code):
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, {})
        return buffer.getvalue()
    except Exception as e:
        return str(e)

# Process prompt
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

                # If response contains a Python block, run it
                if "```python" in msg:
                    st.markdown(msg)
                    code_blocks = [b.split("```")[0] for b in msg.split("```python")[1:]]
                    for block in code_blocks:
                        result = run_code_block(block.strip())
                        st.code(result)
                else:
                    st.markdown(msg)

                if use_voice:
                    speak(msg)

                st.session_state.messages.append({"role": "assistant", "content": msg})
            except Exception as e:
                st.error(f"Error: {e}")
