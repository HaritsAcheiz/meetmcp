import streamlit as st
import asyncio
import os
import json
import datetime
import nest_asynio
from PIL import Image, ImageOps, ImageDraw
from streamlit.components.v1 import html

# Allow asyncio event loop reuse (Streamlit apps rerun on input changes)
nest_asynio.apply()

# =========================== Session Init =============================
if 'conversation' not in st.session_state:
	st.session_state.conversation = []

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


