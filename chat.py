# chat.py

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_core.runnables.history import RunnableWithMessageHistory
from space_management import get_session_history



conversation_memory = []

# Function to update and retrieve memory
def update_memory(new_message):
    global conversation_memory
    conversation_memory.append(new_message)
    # Keep only the last 4 conversations
    if len(conversation_memory) > 4:
        conversation_memory = conversation_memory[-4:]
    return conversation_memory


def get_prompt_for_file_type(file_type):
    prompts = {
        "interview": ChatPromptTemplate.from_messages([
            ("system", "You are an assistant for interview question-answering tasks. Use the following pieces of retrieved context to answer the question. Provide a detailed and informative answer based on the document."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]),
        "financial": ChatPromptTemplate.from_messages([
            ("system", "You are an assistant for financial analysis. Provide detailed responses based on the context retrieved from the document. along with response mention reference page number from document."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]),
        "interior_design": ChatPromptTemplate.from_messages([
            ("system", "You are an assistant for interior design queries. Provide answers based on the context retrieved from the document, focusing on design aspects."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]),
    }
    return prompts.get(file_type, ChatPromptTemplate.from_messages([
        ("system", "I don't know about this domain based on the document provided. Please provide a general response."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]))

def setup_chatbot(llm, vectordb, file_type):
    prompt_template = get_prompt_for_file_type(file_type)
    
    history_aware_retriever = create_history_aware_retriever(
        llm, vectordb.as_retriever(), prompt_template
    )
    
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer the question. "
        "give the reference of page number of answer"
        "If the retrieved context is empty or the question does not belong to interview preparation, "
        "you can give the answer of general mannerful like reply of hii and good morning"
        "respond with 'I don't know the answer to that based on the document.' "
        "Provide a detailed and informative answer based on the document."
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational_rag_chain