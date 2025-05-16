
import streamlit as st
import openai
import os
import tempfile
import io
import contextlib

# --- CONFIG ---
st.set_page_config(page_title="Superchat+", layout="wide")

# --- THEMING ---
theme = st.sidebar.radio("🎨 Choose Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("<style>body { background-color: #111; color: white; }</style>", unsafe_allow_html=True)

# --- MEMORY SYSTEM (SESSION ONLY) ---
if "memory" not in st.session_state:
    st.session_state.memory = []

# --- PLUGINS (Simulated Drag-Drop) ---
st.sidebar.title("🧩 Plugins")
plugin_choice = st.sidebar.selectbox("Select Plugin", ["None", "🧮 Calculator", "📊 Emoji Picker"])
if plugin_choice == "🧮 Calculator":
    st.sidebar.write("Enter an expression:")
    expr = st.sidebar.text_input("Expression", "2 + 2")
    try:
        st.sidebar.success(f"Result: {eval(expr)}")
    except:
        st.sidebar.error("Invalid expression")
elif plugin_choice == "📊 Emoji Picker":
    emoji = st.sidebar.selectbox("Pick Emoji", ["😀", "🔥", "🚀", "💡"])
    st.sidebar.write(f"You picked: {emoji}")

# --- OPENAI KEY ---
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.warning("Please set your OpenAI API key in the environment or Streamlit secrets.")
    st.stop()

st.markdown("<h1 style='text-align: center;'>🧠 Superchat+</h1>", unsafe_allow_html=True)

# --- VOICE TO TEXT INPUT (browser-based) ---
st.markdown("""
<script>
function record() {
  var recognition = new webkitSpeechRecognition();
  recognition.lang = 'en-US';
  recognition.onresult = function(event) {
    const result = event.results[0][0].transcript;
    const inputBox = window.parent.document.querySelectorAll('[contenteditable="true"]')[0];
    if (inputBox) {
      inputBox.innerText = result;
    }
  }
  recognition.start();
}
</script>
<button onclick="record()">🎤 Speak</button>
""", unsafe_allow_html=True)

# --- FILE UPLOAD ---
file_uploaded = st.sidebar.file_uploader("📂 Upload a File (text)")
if file_uploaded:
    st.subheader("📖 Uploaded File Contents:")
    content = file_uploaded.read().decode("utf-8", errors="ignore")
    st.text_area("File Preview", content, height=200)

# --- CHAT SYSTEM ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Say something to Superchat...")

# Text-to-speech output
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

# Python execution block
def run_code_block(code):
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            exec(code, {})
        return buffer.getvalue()
    except Exception as e:
        return str(e)

if prompt:
    st.session_state.memory.append(prompt)  # store to memory
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

                # Run code blocks
                if "```python" in msg:
                    st.markdown(msg)
                    code_blocks = [b.split("```")[0] for b in msg.split("```python")[1:]]
                    for block in code_blocks:
                        result = run_code_block(block.strip())
                        st.code(result)
                else:
                    st.markdown(msg)

                speak(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            except Exception as e:
                st.error(f"Error: {e}")
