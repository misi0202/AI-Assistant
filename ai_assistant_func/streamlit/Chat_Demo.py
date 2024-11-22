import os, sys
import asyncio
import streamlit as st
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from stream_agent import chat_with_user

# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", type="password")

st.set_page_config(
    page_title="对话",
    page_icon="👋",
)
st.sidebar.success("选择功能")

st.title("AI助教系统")
st.caption("🚀 东华大学AI助教系统 demo by赵悦然")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "你好，我是AI助教，有什么可以帮助你的吗？"}]

for msg in st.session_state.messages:
    # 如果msg是字典，就显示消息
    if isinstance(msg, dict):
        st.chat_message(msg["role"]).write(msg["content"])

chat_history = []
# 从聊天框中获取输入
if user_input := st.chat_input():
    # 在messages中添加用户输入
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    chat_history.extend([{"role": "user", "content": user_input}])
    chunks, response, _ = asyncio.run(chat_with_user(user_input=user_input, chat_history=chat_history))
    st.session_state.messages.append({"role": "assistant", "content": response})
    chat_history.extend([{"role": "assistant", "content": response}])
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "reference", "content": chunks})
    st.chat_message("reference").write(chunks)