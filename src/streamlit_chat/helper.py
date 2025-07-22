import streamlit as st
from dotenv import load_dotenv
from personal_helper.chatbot import graph
import logging

load_dotenv()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

def response_generator(prompt):
    stream = graph.stream({"role": "user", "messages": st.session_state.messages[-5:] + [prompt]}, stream_mode="messages")
    for message_chunk, metadata  in stream:
        if metadata["langgraph_node"] == "llm_call_router" or metadata["langgraph_node"] == "categorize_request":
            continue
        if message_chunk.content:
            yield message_chunk.content
            
# Display assistant response in chat message container
with st.chat_message("assistant"):
    if prompt is not None:
        response = st.write_stream(response_generator(prompt))
        st.session_state.messages.append({"role": "assistant", "content": response})
