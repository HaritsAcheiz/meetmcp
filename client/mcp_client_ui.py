import streamlit as st
import os
import json
import datetime
from PIL import Image
import requests
from dotenv import load_dotenv
from uuid import uuid4

# =========================== Function Definition =========================


# Function to load external CSS from static folder
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Log
def add_log(message: str):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f'{timestamp} - {message}'
    st.session_state.logs.append(log_message)
    print(log_message)


def process_query_n8n(query: str) -> str:
    add_log('Sending query to n8n workflow')
    # try:
    # Generate or use existing session ID
    if 'sessionId' not in st.session_state:
        st.session_state.sessionId = str(uuid4()).replace("-", "")[:32]

    # Create the new payload structure
    payload = {
        "sessionId": st.session_state.sessionId,
        "action": "sendMessage",
        "chatInput": query
    }

    add_log(f"Sending payload: {json.dumps(payload, indent=2)}")

    response = requests.post(
        os.getenv('N8N_WEBHOOK_TEST_HOST'),
        json=payload,
        timeout=30
    )
    print(response.content)
    response.raise_for_status()
    result = response.json()
    add_log(f'Received response: {json.dumps(result, indent=2)}')

    # Handle response - adjust based on your n8n's return format
    if isinstance(result, list) and len(result) > 0:
        return result[0].get('output', result[0].get('response', 'No response received'))
    return str(result)

    # except Exception as e:
    #     add_log(f'Error calling n8n: {str(e)}')
    #     return "Sorry, I encountered an error processing your request."


def handle_query(query: str):
    if query.strip().lower() == 'quit':
        st.session_state.conversations = {'default': []}
        st.session_state.context = {}
        st.session_state.active_chat = 'default'
        add_log('Conversation')
    else:
        user_msg = {
            'sender': 'User',
            'message': query,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'user_message'
        }

        if st.session_state.active_chat not in st.session_state.conversations:
            st.session_state.conversations[st.session_state.active_chat] = []

        st.session_state.conversations[st.session_state.active_chat].append(user_msg)
        st.session_state.conversation_modified = True
        add_log(f'User query appended: {query}')

        response_data = process_query_n8n(query)  # Now synchronous

        assistant_msg = {
            'sender': 'Assistant',
            'message': response_data.get('text', '') if isinstance(response_data, dict) else response_data,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'response'
        }
        st.session_state.conversations[st.session_state.active_chat].append(assistant_msg)
        st.session_state.query_executed = True
        st.session_state.last_query = query


# Set the submit_triggered flag when nter is pressed
def submit_on_enter():
    if st.session_state.query_input.strip() and not st.session_state.get('prevent_rerun', False):
        st.session_state.submit_triggered = True
        st.session_state.pending_query = st.session_state.query_input
        st.session_state.prevent_rerun = True
        st.session_state.query_input = ""


# ===========================  Initialization =============================

load_dotenv('../.env')
load_css()

# Set Parameters
conversations_dir = 'conversations'

# Set session state
if 'conversations' not in st.session_state:
    st.session_state.conversations = {
        'default': []
    }

if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'submit_triggered' not in st.session_state:
    st.session_state.submit_triggered = False

if 'query_executed' not in st.session_state:
    st.session_state.query_executed = False

if 'pending_query' not in st.session_state:
    st.session_state.pending_query = None

if 'active_chat' not in st.session_state:
    st.session_state.active_chat = 'default'

if 'sessionId' not in st.session_state:
    st.session_state.sessionId = str(uuid4()).replace("-", "")[:32]

if 'conversation_modified' not in st.session_state:
    st.session_state.conversation_modified = False

if 'prevent_rerun' not in st.session_state:
    st.session_state.prevent_rerun = False

if 'last_query' not in st.session_state:
    st.session_state.last_query = None

# ============================= UI ==================================

# Sidebar
with st.sidebar:
    st.image('static/deepseek-color.svg', width=250)

    # New Chat button
    new_conv_button = st.button('New Chat', use_container_width=True, key="new_chat")
    if new_conv_button:
        if st.session_state.conversation_modified:
            # Auto-save current conversation if it exists
            if st.session_state.get('conversations'):
                os.makedirs(conversations_dir, exist_ok=True)
                filename = f"conversation_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                filepath = os.path.join(conversations_dir, filename)

                with open(filepath, 'w') as f:
                    json.dump(st.session_state.conversations, f, indent=2)
                add_log(f"Auto-saved conversation as {filename}")

            # Start fresh conversation
            st.session_state.conversations = {'default': []}
            st.session_state.context = {}
            st.session_state.conversation_modified = False
            add_log('New conversation started')
            st.rerun()

    # Chat history list
    st.markdown("### History")
    os.makedirs(conversations_dir, exist_ok=True)
    conversation_files = sorted(
        [f for f in os.listdir(conversations_dir) if f.endswith('.json')],
        key=lambda x: os.path.getmtime(os.path.join(conversations_dir, x)),
        reverse=True
    )

    if conversation_files:
        for filename in conversation_files:
            filepath = os.path.join(conversations_dir, filename)
            # try:
            with open(filepath, 'r') as f:
                conv = json.load(f)

            # Safe preview generation
            preview = 'No messages'
            first_msg = conv['default'][0] if isinstance(conv['default'][0], dict) else {}
            preview = first_msg.get('message', 'No message')[:20]

            # Display load button with timestamp
            file_time = datetime.datetime.fromtimestamp(
                os.path.getmtime(filepath)
            )

            display_name = f"{file_time.strftime('%Y-%m-%d %H:%M')}: {preview}..."

            if st.button(display_name, key=f"hist_{filename}"):
                if isinstance(conv, dict):
                    st.session_state.conversations = conv
                else:
                    st.session_state.conversations = {'default': conv}
                st.session_state.active_chat = 'default'
                add_log(f'Loaded conversation from {filename}')
                st.rerun()

            # except Exception as e:
            #     add_log(f"Error loading {filename}: {str(e)}")
            #     continue
    else:
        st.info('No saved conversations found')

# Main
col1, col2 = st.columns([1, 6])

# Logo
with col1:
    logo = Image.open('static/deepseek-color.png')
    st.image(logo, use_container_width=True)

# Greeting
with col2:
    st.title("Hi, I'm Deepseek.")
    st.markdown('How can I help you today?', unsafe_allow_html=True)

# Display only active messages
active_messages = []
if isinstance(st.session_state.conversations, dict):
    active_messages = st.session_state.conversations.get(st.session_state.active_chat, [])
elif isinstance(st.session_state.conversations, list):
    active_messages = st.session_state.conversations

for msg in active_messages:
    if isinstance(msg, dict):
        timestamp = msg.get('timestamp', '')
        sender = msg.get('sender', '')
        message = msg.get('message', '')
        st.markdown(f'**[{timestamp}] {sender}: ** {message}')

st.text_input(
    'Message Deepseek',
    key='query_input',
    placeholder='Message Deepseek',
    on_change=submit_on_enter
)

send_button = st.button('Send')

# ==================================== Main Trigger Logic ==============================
if (send_button or st.session_state.submit_triggered) and not st.session_state.query_executed:
    query = st.session_state.pending_query.strip()
    if query:
        handle_query(query)
        st.session_state.submit_triggered = False
        st.session_state.prevent_rerun = False
        st.session_state.pending_query = ""
        # st.rerun()


# Rerun app after query complete to refresh the UI
if st.session_state.query_executed:
    st.session_state.query_executed = False
    st.rerun()
