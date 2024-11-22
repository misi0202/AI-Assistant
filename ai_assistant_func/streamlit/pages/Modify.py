import streamlit as st
import os, sys
from utils.knowledge_database import Neo4jUtils

st.set_page_config(page_title="修改知识库")

st.markdown("# 修改知识库")

N4J = Neo4jUtils()
KNOWLEDGE_LIST = N4J.FindAllClass()

knowledge_base: str = st.selectbox("知识库选择", options=KNOWLEDGE_LIST)

BOOK_LIST = N4J.FindAllBook(knowledge_base)
book: str = st.selectbox("书籍选择", options=BOOK_LIST)

CHUNKS = N4J.FindAllChunk(book)

modified_data = []

for idx, item in enumerate(CHUNKS):
    st.subheader(f"Chunk {idx+1}")
    
    # 使用文本框展示并编辑内容
    content = st.text_area(f"内容 ", value=item["content"], key=f"content_{idx}")
    source = st.write(f"来源 : {item['source']}")
    chunkSeqId = st.write(f"Id : {item['chunkSeqId']}")
    
    # 确认按钮
    if st.button(f"确认修改 ", key=f"confirm_{idx}"):
        # 在页面上显示修改前后的文本
        original = CHUNKS[idx]
        # source修改前后不变
        modified = {"source": CHUNKS[idx]["source"],"chunkSeqId": CHUNKS[idx]["chunkSeqId"],"content": content}
        st.write("原文本:", original)
        st.write("修改后文本:", modified)
        
        # 更新数据库

        N4J.UpdateChunk(CHUNKS[idx]["source"],CHUNKS[idx]["chunkSeqId"], content)


