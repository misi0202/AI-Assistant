import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
from utils.knowledge_database import Neo4jUtils
from utils.file_utils import FileUtils

# 标题
st.title("上传 PDF 文件")

N4J = Neo4jUtils()
FileU = FileUtils()
KNOWLEDGE_LIST = N4J.FindAllClass()

knowledge_base: str = st.selectbox("知识库选择", options=KNOWLEDGE_LIST)
# 上传文件控件
uploaded_file = st.file_uploader("上传知识库文件", type="pdf")

if uploaded_file is not None:
    
    
    # 输入框：获取新的文件名
    new_filename = st.text_input("文件名称", value= uploaded_file.name)

    # 确认按钮：提交并处理文件
    if st.button("确认并提交"):
        
        if new_filename:
            # 添加 .pdf 后缀
            new_filename = f"{new_filename}.pdf"
            # 上传文件
            status = FileU.UploadPDFFile(knowledge_base, new_filename, uploaded_file)
            if status:
                st.success("文件上传成功")
            else:
                st.error("文件上传失败")
            

        
        else:
            st.error("Please provide a valid file name.")
    

