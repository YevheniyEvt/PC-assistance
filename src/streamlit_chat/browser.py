import streamlit as st
from dotenv import load_dotenv
from developer_chatbot.chatbot import graph
from open_browser.chatbot import graph as browser_bot

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

if prompt is not None:
    response = browser_bot.invoke({"messages": [prompt]})
    content = response["messages"][-1].content
    with st.chat_message("assistant"):
        st.markdown(content)
    st.session_state.messages.append({"role": "assistant", "content": content})