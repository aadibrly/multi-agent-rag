# note : - if you wanna add this bot to ur costom frontend u can ignore this 
# but make sure you pass thread_id to the fast api  

import uuid
import requests
import streamlit as st

API_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="Synapse~Flow~Assistant", layout="wide")
st.title("Synapse Flow")

#thread id generation
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4()) #genrates 4 len unique ids

if "messages" not in st.session_state:
    st.session_state.messages = []

#Sidebar controls 
with st.sidebar:
    st.header("Settings")
    st.caption(f"Session ID: `{st.session_state.thread_id}`")

    if st.button("+ New Chat"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    provider = st.selectbox("LLM Provider", ["openrouter", "groq", "gemini", "nvidia"])
    model_override = st.text_input("Model Override (optional)", placeholder="e.g. llama-3.3-70b-versatile")
    db_uri = st.text_input("SQL Database URI (optional)", placeholder="sqlite:///./sample.db")
    system_prompt = st.text_area("Custom System Prompt (optional)", placeholder="e.g. You are a fitness Coach.")

# Chat history rendering
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("meta"):
            st.caption(msg["meta"])
        if msg.get("sql_query"):
            with st.expander("Generated Sql Query"):
                st.code(msg["sql_query"], language="sql")

# caht input box 
prompt = st.chat_input("Ask Flow")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", width="content", avatar= "😶"):
        st.markdown(prompt)

    payload = {
        "query" : prompt,
        "thread_id" : st.session_state.thread_id,
        "provider" : provider,
        "model_override" : model_override.strip() or None,
        "db_uri" : db_uri.strip() or None,
        "system_prompt" : system_prompt.strip() or None,
    }

    with st.chat_message("ai", width="content", avatar="🙂"):
        with st.spinner("Using Brain...."):
            try:
                response =  requests.post(API_URL, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()

                answer = data.get("final_answer", "")
                route = data.get("route", "unknown")
                sql_query = data.get("sql_query")
                meta_text = f"Route: `{route.upper()}` | Provider: `{provider}`"

                st.markdown(answer)
                st.caption(meta_text)

                if sql_query:
                    with st.expander("Generated SQL Query"):
                        st.code(sql_query, language="sql")

                st.session_state.messages.append({
                    "role":"assistant",
                    "content": answer,
                    "meta": meta_text,
                    "sql_query": sql_query,
                })
            except requests.exceptions.RequestException as exe:
                st.error(f"API ERROR: {exe}") 