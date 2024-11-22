import streamlit as st
from utils.knowledge_database import Neo4jUtils
st.title("创建课程")

user_input = st.text_input("请输入课程名称")

# 提交按钮
if st.button("提交表单"):
    
    if user_input:
        N4J = Neo4jUtils()
        status = N4J.CreateCourse(user_input)
        st.success(f"成功创建“{user_input}”课程")
    else:
        # 如果输入为空，显示失败消息
        st.error("请输入文字")
