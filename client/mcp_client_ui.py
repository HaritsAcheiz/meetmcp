import streamlit as st
import asyncio
import os
import json
import datetime
import nest_asyncio
from PIL import Image, ImageOps, ImageDraw
from streamlit.components.v1 import html

# Allow asyncio event loop reuse (Streamlit apps rerun on input changes)
nest_asyncio.apply()


# Function to load external CSS from static folder
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Call the function
load_css()

# ===========================  Initialization =============================
if 'conversation' not in st.session_state:
    st.session_state.conversations = []

if 'client_config' not in st.session_state:
    st.session_state.client_config = {
        'client_type': 'STDIO',
        'server_url': ''
    }

if 'client_instance' not in st.session_state:
    st.session_state.client_instance = None

if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'submit_triggered' not in st.session_state:
    st.session_state.submit_triggered = False

if 'query_executed' not in st.session_state:
    st.session_state.query_executed = False

if 'pending_query' not in st.session_state:
    st.session_state.pending_query = ''


# ========================= Utility Function ============================
def run_async_in_event_loop(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


# ============================== Log ====================================
def add_log(message: str):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f'{timestamp} - {message}'
    st.session_state.logs.append(log_message)
    print(log_message)


# ============================= Sidebar ==================================
with st.sidebar:
    st.image('static/deepseek-color.svg', width=300)

    st.session_state.client_config['client_type'] = "STDIO"
    add_log(f'Client type set to STDIO')

    config_path = 'config.json'
    if os.path.exists(config_path):
        st.session_state.client_config['stdio_config'] = config_path
        add_log(f'Using config {config_path}')
    else:
        add_log('Config is not found')

    # New Chat button
    if st.button("New Chat", use_container_width=True, key="new_chat"):
        new_chat_id = f"chat_{len(st.session_state.chat_history) + 1}"
        st.session_state.chat_history.append({
            "id": new_chat_id,
            "title": f"Chat {len(st.session_state.chat_history) + 1}",
            "messages": []
        })
        st.session_state.active_chat = new_chat_id
        st.rerun()

    # Chat history list
    st.markdown("### History")
    conversations_dir = 'conversations'
    os.makedirs(conversations_dir, exist_ok=True)
    conversation_files = os.listdir(conversations_dir)

    if conversation_files:
        for filename in conversation_files:
            filepath = os.path.join(conversations_dir, filename)
            with open(filepath, 'r') as f:
                conv = json.load(f)
            preview = conv[0]['message'][:20] if conv else 'No message'
            if st.button(f'Load {filename}'):
                st.session_state.conversations = conv
                add_log(f'Load  conversation from {filename}')
                st.rerun()
    else:
        st.info('No saved conversations found')

# ============================== Main Chat UI ====================================
col1, col2 = st.columns([1, 6])
with col1:
    logo = Image.open('static/deepseek-color.png')
    # size = min(logo.size)
    # mask = Image.new('L', (size, size), 0)
    # draw = ImageDraw.Draw(mask)
    # draw.ellipse((0, 0, size, size), fill=255)
    # circular_logo = ImageOps.fit(logo, (size, size), centering=(0.5, 0.5))
    # circular_logo.putalpha(mask)
    st.image(logo, use_container_width=True)

with col2:
    st.title("Hi, I'm Deepseek.")
    st.markdown('How can I help you today?', unsafe_allow_html=True)

# Show past conversations
for msg in st.session_state.conversations:
    timestamp = msg.get('timestamp', '')
    sender = msg.get('sender', '')
    message = msg.get('message', '')
    st.markdown(f'**[{timestamp}] {sender}: ** {message}')


# Set the submit_triggered flag when nter is pressed
def submit_on_enter():
    if st.session_state.query_input.strip():
        st.session_state.submit_triggered = True
        st.session_state.pending_query = st.session_state.query_input


st.text_input('Message Deepseek')