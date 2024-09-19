# space_management.py

import os
import json
import time
import psutil
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
    new_space_id = space_description

    if new_space_id in st.session_state['spaces']:
        st.error("Space with this description already exists.")
        return

    current_directory = os.getcwd()
    try:
        persist_directory_folder = os.path.join(current_directory, f'.\chroma_persistence2_{new_space_id}')

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
    save_space(new_space_id)
    save_chat_history(session_id)
    save_all_spaces()
    st.success(f"Space '{space_description}' created successfully with files: {', '.join(valid_files)}!")

def switch_space(space_name):
    if space_name in st.session_state['spaces']:
        st.session_state['current_space'] = space_name
        load_chat_history(st.session_state.get('session_id', ''))
        save_space(st.session_state.get('session_id', ''))
    else:
        st.error(f"Space '{space_name}' does not exist.")


def close_open_files(directory):
    for proc in psutil.process_iter():
        try:
            # Iterate through all file descriptors used by this process
            for f in proc.open_files():
                if directory in f.path:
                    print(f"Terminating process holding file: {f.path}")
                    proc.terminate()  # Close process if it holds an open file in the directory
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue


def delete_space(space_name):
    space_info = st.session_state['spaces'].get(space_name)
    if space_info and 'chroma_directory' in space_info:
        shutil.rmtree(space_info['chroma_directory'])

    if space_name in st.session_state['spaces']:
        del st.session_state['spaces'][space_name]

    if st.session_state['current_space'] == space_name:
        st.session_state['current_space'] = None
        st.session_state.messages = []
    
    chat_history_file = f"{st.session_state.get('session_id', '')}_chat_history.json"
    if os.path.exists(chat_history_file):
        os.remove(chat_history_file)
    st.success(f"Space '{space_name}' deleted successfully!")

def save_space(space_id):
    if space_id in st.session_state['spaces']:
        file_path = f'{space_id}_space.json'
        with open(file_path, 'w') as f:
            json.dump(st.session_state['spaces'][space_id], f)
    else:
        st.error(f"Space with ID '{space_id}' does not exist.")


def load_space(space_id):
    file_path = f'{space_id}_space.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            st.session_state['spaces'][space_id] = json.load(f)
    else:
        st.session_state['spaces'][space_id] = {}

def save_all_spaces():
    with open("all_spaces.json", 'w') as f:
        json.dump(st.session_state['spaces'], f)

def load_all_spaces():
    if os.path.exists("all_spaces.json"):
        with open("all_spaces.json", 'r') as f:
            st.session_state['spaces'] = json.load(f)
    else:
        st.session_state['spaces'] = {}

def save_chat_history(session_id):
    if 'messages' in st.session_state:
        chat_history_file = f'{session_id}_chat_history.json'
        with open(chat_history_file, 'w') as f:
            json.dump(st.session_state.messages, f)

def load_chat_history(session_id):
    chat_history_file = f'{session_id}_chat_history.json'
    if os.path.exists(chat_history_file):
        with open(chat_history_file, 'r') as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

def get_session_history(session_id):
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]