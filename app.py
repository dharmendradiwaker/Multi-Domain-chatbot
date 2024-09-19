import streamlit as st
from config import GROQ_API_KEY
from chat import setup_chatbot, update_memory
from langchain_groq import ChatGroq
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from space_management import save_user_data, save_chat_history, load_chat_history, load_chat_history, load_all_spaces, switch_space, delete_space, save_space, load_space, create_new_space, get_user_spaces


# Initialize models
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

# Initialize spacesload_user_spaces
if 'spaces' not in st.session_state:
    st.session_state['spaces'] = {}

if 'current_space' not in st.session_state:
    st.session_state['current_space'] = None

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = None

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'show_history' not in st.session_state:
    st.session_state['show_history'] = False

def main():
    st.title("Chatbot")
    st.markdown("""**Disclaimer:** This chatbot is designed to assist with interview preparation, financial data analysis, 
    and interior design-related queries. It may not be suitable for other purposes. Please use the chatbot within these domains for the best experience.""")

    if not st.session_state.get('user_name') or not st.session_state.get('user_email'):
        with st.sidebar.form(key='user_info_form'):
            user_name = st.text_input("Enter your name")
            user_email = st.text_input("Enter your email")
            submit_user_info = st.form_submit_button("Submit Info")

            if submit_user_info:
                if user_name and user_email:
                    st.session_state['user_name'] = user_name
                    st.session_state['user_email'] = user_email
                    st.session_state['session_id'] = f"{user_name}_{user_email}"
                    
                    # Save user data
                    save_user_data(user_name, user_email)
                    st.session_state['spaces'] = get_user_spaces(user_email)
                    load_all_spaces()
                    st.success("Information saved successfully.")
                    st.rerun()  # Refresh to show the space management section
                else:
                    st.error("Please provide both name and email.")
        return

    # Load all spaces after user information is saved
    if 'spaces' not in st.session_state:
        st.session_state['spaces'] = {}
        load_all_spaces()

    if 'show_history' not in st.session_state:
        st.session_state['show_history'] = False

    # Sidebar for managing spaces (only after user info is provided)
    st.sidebar.title(f"Welcome, {st.session_state['user_name']}!")
    st.sidebar.header("Your Spaces")

    # Load user's spaces for dropdown
    user_spaces = get_user_spaces(st.session_state['user_email'])
    
    if user_spaces:
        for space_name in user_spaces:
            if space_name in st.session_state['spaces']:
                space_info = st.session_state['spaces'][space_name]
                st.sidebar.write(f"Space: {space_name}")
                st.sidebar.write(f"Description: {space_info.get('description', 'No description')}")
    
    st.sidebar.header("Space Management")

    with st.sidebar.form(key='create_space_form'):
        space_description = st.text_input("Space Description")
        uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)
        submit_button = st.form_submit_button(label='Create Space')
        
        if submit_button:
            if space_description and uploaded_files:
                create_new_space(space_description, uploaded_files, embedding_model)
            else:
                st.error("Please provide a space description and upload at least one file.")

    with st.sidebar.expander("Switch or Delete Space"):
        selected_space = st.selectbox("Select Space", options=list(st.session_state['spaces'].keys()) + ["None"])
        if selected_space != st.session_state.get('current_space'):
            switch_space(selected_space)
        if st.button("Delete", key=f"delete_{selected_space}"):
            delete_space(selected_space)

    st.sidebar.header("Chat History")
    if st.sidebar.button("Show Chat History"):
        st.session_state['show_history'] = not st.session_state['show_history']  # Toggle history view

    if st.session_state['current_space']:
        space_info = st.session_state['spaces'][st.session_state['current_space']]
        vectordb = Chroma(persist_directory=space_info['chroma_directory'], embedding_function=embedding_model)
        file_types = space_info.get('file_types', {})
        file_type = next(iter(file_types.values()), "unknown")
        rag_chain = setup_chatbot(llm, vectordb, file_type)
        current_space = st.session_state['current_space']
        st.title(f"{st.session_state['spaces'][current_space]['description']}")
        st.write(f"Selected Space: {current_space}")
        
        if user_prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": user_prompt})

            with st.chat_message("user"):
                st.markdown(user_prompt)
            
            with st.chat_message("assistant"):
                memory = update_memory(user_prompt)
                response = rag_chain.invoke(
                    {"input": user_prompt,
                     "chat_history": memory},
                    config={"configurable": {"session_id": st.session_state.get('session_id', '')}}
                )["answer"]
                
                st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                save_chat_history(st.session_state.get('session_id', ''), st.session_state['current_space'])  # Save chat history for the session
                save_space(st.session_state['current_space'])

        if st.session_state['show_history']:
            st.header("Chat History")
            # Display the chat history at the bottom or in a separate section
            for message in st.session_state.messages:
                role = message.get("role", "unknown")
                content = message.get("content", "")
                with st.chat_message(role):
                    st.markdown(content)
if __name__ == "__main__":
    main()