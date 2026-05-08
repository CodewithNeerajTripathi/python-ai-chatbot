import streamlit as st
import os
from dotenv import load_dotenv   # ← ADD THIS
from groq import Groq

load_dotenv()                    # ← ADD THIS

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.title("My AI Chatbot")

if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "system",
            "content": "You are a Python coding expert. Only answer questions about Python code. If someone asks anything else politely say - I can only help with Python related questions."
        }
    ]

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Type your message here")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.history.append({
        "role": "user",
        "content": user_input
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=st.session_state.history
    )

    reply = response.choices[0].message.content

    with st.chat_message("assistant"):
        st.write(reply)

    st.session_state.history.append({
        "role": "assistant",
        "content": reply
    })