# space_management.py

import os
import json
import time
import shutil
import tempfile
import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory

store = {}
def create_new_space(space_description, uploaded_files, embedding_model):
    if 'session_id' not in st.session_state:
        st.error("Please provide your name and email.")
        return
    session_id = st.session_state['session_id']
    user_email = st.session_state.get('user_email', None)
    if not user_email:
        st.error("User email is not set.")
        return
    # Ensure spaces are initialized in session state
    if 'spaces' not in st.session_state:
        st.session_state['spaces'] = {}

    new_space_id = space_description

    if new_space_id in st.session_state['spaces']:
        st.error("Space with this description already exists.")
        return

    current_directory = os.getcwd()
    directory = 'chroma_vector'
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        persist_directory_folder = os.path.join(directory, f'.\chroma_persistence_{new_space_id}')

    except Exception as e:
        print("error in saving persisting file path")
        print(e)

    if os.path.exists(persist_directory_folder):
        print(f"Removing existing directory: {persist_directory_folder}")
        try:
            shutil.rmtree(persist_directory_folder)
        except PermissionError as e:
            print(f"PermissionError: {e}")
            time.sleep(1)  # Delay before retrying
            try:
                shutil.rmtree(persist_directory_folder)
            except Exception as e:
                st.error(f"Failed to remove directory: {e}")
                return
    
    os.makedirs(persist_directory_folder, exist_ok=True)
    print(f"Directory created: {persist_directory_folder}")  # Debugging line

    file_types = {}
    valid_files = []

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name.lower()

        if "interview" in file_name:
            file_type = "interview"
        elif "financial" in file_name:
            file_type = "financial"
        elif "interior" in file_name:
            file_type = "interior_design"
        else:
            st.warning(f"File '{uploaded_file.name}' does not match any category criteria. It will be ignored.")
            continue
        
        file_types[uploaded_file.name] = file_type

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        
        loader = PyPDFLoader(temp_file_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        vectordb = Chroma(embedding_function=embedding_model, persist_directory=persist_directory_folder)
        vectordb.add_documents(documents=splits)
        # vectordb.persist()

        valid_files.append(uploaded_file.name)
    
    if not valid_files:
        st.error("No valid files were uploaded. Please upload files that match the criteria.")
        return

    st.session_state['spaces'][new_space_id] = {
        'description': space_description,
        'chroma_directory': persist_directory_folder,
        'chat_history': [],
        'file_types': file_types
    }
    
    st.session_state['current_space'] = new_space_id
    st.session_state.messages = []
    save_user_data(st.session_state['user_name'], st.session_state['user_email'])
    save_chat_history(session_id, new_space_id)
    save_all_spaces()
    st.success(f"Space '{space_description}' created successfully with files: {', '.join(valid_files)}!")

def save_space(space_id):
    if space_id not in st.session_state['spaces']:
        st.error(f"Space '{space_id}' does not exist.")
        return
    directory = 'spaces_data'
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f'{space_id}_space.json')
    with open(file_path, 'w') as f:
        json.dump(st.session_state['spaces'][space_id], f, indent=4)


def switch_space(space_name):
    if space_name not in st.session_state['spaces']:
        st.error(f"Space '{space_name}' does not exist.")
        return

    st.session_state['current_space'] = space_name
    session_id = st.session_state.get('session_id', '')

    if session_id:
        load_chat_history(session_id, space_name)
    else:
        st.error("Session ID is missing. Unable to load chat history.")

    save_space(space_name)


import time

def delete_space(space_name):
    space_info = st.session_state['spaces'].get(space_name)
    if space_info and 'chroma_directory' in space_info:
        shutil.rmtree(space_info['chroma_directory'])
    
    # Remove space from session state
    if space_name in st.session_state['spaces']:
        del st.session_state['spaces'][space_name]
    if st.session_state['current_space'] == space_name:
        st.session_state['current_space'] = None
        st.session_state.messages = []

    chat_history_file = f"{st.session_state.get('session_id', '')}_chat_history.json"
    if os.path.exists(chat_history_file):
        os.remove(chat_history_file)
    st.success(f"Space '{space_name}' deleted successfully!")


def load_space(space_id):
    directory = 'spaces_data'
    file_path = os.path.join(directory, f'{space_id}_space.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            st.session_state['spaces'][space_id] = json.load(f)
    else:
        st.session_state['spaces'][space_id] = {}


def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def save_user_data(user_name, user_email):
    user_data_file = 'users.json'
    user_data = load_user_data()
    
    # Initialize user data if not present
    if user_email not in user_data:
        user_data[user_email] = {'name': user_name, 'spaces': {}}
    
    # Preserve existing spaces
    existing_spaces = user_data[user_email]['spaces']
    
    # Update spaces with current session data without removing existing spaces
    updated_spaces = {**existing_spaces, **st.session_state.get('spaces', {})}
    
    user_data[user_email]['spaces'] = updated_spaces
    
    # Save updated user data
    with open(user_data_file, 'w') as f:
        json.dump(user_data, f, indent=4)

def load_user_data():
    user_data_file = 'users.json'
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as f:
            return json.load(f)
    return {}

def get_user_spaces(user_email):
    user_data = load_user_data()
    return user_data.get(user_email, {}).get('spaces', {})

def save_chat_history(session_id, space_id):
    if 'messages' in st.session_state:
        directory = 'chat_history_data'
        if not os.path.exists(directory):
            os.makedirs(directory)  # Create the directory if it does not exist
        # Use both session_id and space_id to ensure unique file paths
        chat_history_file = os.path.join(directory, f'{space_id}_{session_id}_chat_history.json')
        with open(chat_history_file, 'w') as f:
            json.dump(st.session_state.messages, f)



def load_chat_history(session_id, space_id):
    directory = 'chat_history_data'
    # Use both session_id and space_id to ensure the correct file is loaded
    chat_history_file = os.path.join(directory, f'{space_id}_{session_id}_chat_history.json')
    if os.path.exists(chat_history_file):
        with open(chat_history_file, 'r') as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []


def save_all_spaces():
    user_email = st.session_state.get('user_email')
    if user_email:
        user_data = load_user_data()
        if user_email in user_data:
            user_data[user_email]['spaces'] = st.session_state['spaces']
            with open('users.json', 'w') as f:
                json.dump(user_data, f, indent=4)


def load_all_spaces():
    user_email = st.session_state.get('user_email')
    if user_email:
        user_data = load_user_data()
        if user_email in user_data:
            st.session_state['spaces'] = user_data[user_email].get('spaces', {})
        else:
            st.session_state['spaces'] = {}
    else:
        st.session_state['spaces'] = {}

