# import streamlit as st
# from ollama import chat

# # Initialize Streamlit app
# st.set_page_config(page_title="Ollama Chatbot", layout="centered")
# st.title("🤖 Ollama Chatbot")

# # Maintain session state for conversation history
# if "conversation_history" not in st.session_state:
#     st.session_state["conversation_history"] = []

# # Function to get response from Ollama
# def get_response(messages):
#     response = ""
#     for chunk in chat(model="llama3.2", messages=messages, stream=True):
#         response += chunk["message"]["content"]
#         yield response

# # Sidebar for starting a new conversation
# if st.sidebar.button("Start New Conversation"):
#     st.session_state["conversation_history"] = []
#     st.success("Started a new conversation!")

# # Display conversation history
# for message in st.session_state["conversation_history"]:
#     if message["role"] == "user":
#         st.chat_message("user").markdown(message["content"])
#     else:
#         st.chat_message("assistant").markdown(message["content"])

# # User input
# user_message = st.chat_input("Type your message:")

# # Send message and display chat
# if user_message:
#     # Append user message to conversation history
#     st.session_state["conversation_history"].append({"role": "user", "content": user_message})

#     # Display user message in the chat
#     st.chat_message("user").markdown(user_message)

#     # Call Ollama and stream the response
#     response_placeholder = st.empty()
#     response = ""
#     for partial_response in get_response(st.session_state["conversation_history"]):
#         response = partial_response
#         response_placeholder.chat_message("assistant").markdown(response)

#     # Append the bot's response to conversation history
#     st.session_state["conversation_history"].append({"role": "assistant", "content": response})


# import streamlit as st
# from ollama import chat
# import PyPDF2
# import io

# # Initialize Streamlit app
# st.set_page_config(page_title="Ollama Chatbot", layout="centered")
# st.title("🤖 Ollama Chatbot")

# # Maintain session state for conversation history
# if "conversation_history" not in st.session_state:
#     st.session_state["conversation_history"] = []

# # Function to extract text from PDF
# def extract_pdf_text(pdf_file):
#     pdf_reader = PyPDF2.PdfReader(pdf_file)
#     text = ""
#     for page in pdf_reader.pages:
#         text += page.extract_text()
#     return text

# # Function to get response from Ollama
# def get_response(messages):
#     response = ""
#     for chunk in chat(model="llama3.2", messages=messages, stream=True):
#         response += chunk["message"]["content"]
#         yield response

# # Sidebar for starting a new conversation
# if st.sidebar.button("Start New Conversation"):
#     st.session_state["conversation_history"] = []
#     st.success("Started a new conversation!")

# # Display conversation history
# for message in st.session_state["conversation_history"]:
#     if message["role"] == "user":
#         st.chat_message("user").markdown(message["content"])
#     else:
#         st.chat_message("assistant").markdown(message["content"])

# # File uploader for PDF
# uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
# pdf_text = ""

# if uploaded_file is not None:
#     pdf_text = extract_pdf_text(uploaded_file)
#     st.success("PDF uploaded and processed successfully!")

# # User input
# user_message = st.chat_input("Type your message:")

# # Send message and display chat
# if user_message:
#     # Combine PDF content with user message if PDF was uploaded
#     if pdf_text:
#         combined_message = f"PDF Content: {pdf_text}\n\nUser Question: {user_message}"
#     else:
#         combined_message = user_message

#     # Append user message to conversation history
#     st.session_state["conversation_history"].append({"role": "user", "content": user_message})

#     # Display user message in the chat
#     st.chat_message("user").markdown(user_message)

#     # Call Ollama and stream the response
#     response_placeholder = st.empty()
#     response = ""
    
#     messages = [{"role": "user", "content": combined_message}]
#     for partial_response in get_response(messages):
#         response = partial_response
#         response_placeholder.chat_message("assistant").markdown(response)

#     # Append the bot's response to conversation history
#     st.session_state["conversation_history"].append({"role": "assistant", "content": response})


# ... existing code ...
import streamlit as st
from ollama import chat
import PyPDF2
import io
from typing import List

# Initialize Streamlit app
st.set_page_config(page_title="Ollama Chatbot", layout="centered")
st.title("🤖 Ollama Chatbot")

# Function to split text into chunks of specified size
def split_text_into_chunks(text: str, chunk_size: int = 2000) -> List[str]:
    """Split text into chunks of approximately chunk_size characters."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for the space
        if current_length + word_length > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length
            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks

# Function to extract text from PDF
def extract_pdf_text(pdf_file) -> str:
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to get response from Ollama
def get_response(messages):
    response = ""
    for chunk in chat(model="llama3.2", messages=messages, stream=True):
        response += chunk["message"]["content"]
        yield response

# Maintain conversation history
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

# Sidebar for starting a new conversation
if st.sidebar.button("Start New Conversation"):
    st.session_state["conversation_history"] = []
    st.success("Started a new conversation!")

# Display conversation history
for message in st.session_state["conversation_history"]:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["content"])
    else:
        st.chat_message("assistant").markdown(message["content"])

# File uploader for PDF
uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
pdf_chunks = []

if uploaded_file is not None:
    # Extract text from PDF
    pdf_text = extract_pdf_text(uploaded_file)
    
    # Split into chunks
    pdf_chunks = split_text_into_chunks(pdf_text)
    st.success(f"PDF uploaded and processed into {len(pdf_chunks)} chunks")

# User input
user_message = st.chat_input("Type your message:")

# Send message and display chat
if user_message:
    # Append user message to conversation history
    st.session_state["conversation_history"].append({"role": "user", "content": user_message})
    
    # Display user message
    st.chat_message("user").markdown(user_message)
    
    # Process each PDF chunk separately if PDF was uploaded
    if pdf_chunks:
        combined_response = ""
        progress_bar = st.progress(0)
        
        for i, chunk in enumerate(pdf_chunks):
            # Combine the chunk with user's question
            chunk_prompt = f"PDF Content Chunk {i+1}/{len(pdf_chunks)}:\n{chunk}\n\nUser Question: {user_message}"
            
            # Get response for this chunk
            messages = [{"role": "user", "content": chunk_prompt}]
            
            # Update progress bar
            progress_bar.progress((i + 1)/len(pdf_chunks))
            
            # Get and accumulate response
            for partial_response in get_response(messages):
                response = partial_response
                combined_response += response + "\n\n"
                
        # Display final combined response
        st.chat_message("assistant").markdown(combined_response)
        progress_bar.empty()
        
        # Add to conversation history
        st.session_state["conversation_history"].append({
            "role": "assistant", 
            "content": combined_response
        })
    
    else:
        # Regular chat without PDF
        messages = [{"role": "user", "content": user_message}]
        response_placeholder = st.empty()
        
        for partial_response in get_response(messages):
            response = partial_response
            response_placeholder.chat_message("assistant").markdown(response)
        
        st.session_state["conversation_history"].append({
            "role": "assistant",
            "content": response
        })