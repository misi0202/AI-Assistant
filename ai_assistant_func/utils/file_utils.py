from langchain_community.graphs import Neo4jGraph
import os, sys
from utils_base import BaseUtils
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from io import BytesIO
from tqdm import *
import fitz  # PyMuPDF
from extract.extract_pdf import extract_toc_content, embedding_text, generate_cypher

load_dotenv("E:\\py_code\\course_assistant\\.env")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
embedding_key = os.getenv("EMBEDDING_KEY")
embedding_name = os.getenv("EMBEDDING_NAME")

class FileUtils(BaseUtils):
    def __init__(self) -> None:
        # 注册数据库连接
        self.kg = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE)
        self.emedding_model = ZhipuAI(api_key = embedding_key)
        self.embedding_name = embedding_name
        return super().__init__()

    def UploadPDFFile(self, course_name, file_name, uploaded_file):
        """传入pdf文件的输入流 根据课程名称 上传至知识库"""
        # 读取 PDF 文件的二进制内容
        print(f"Uploading {file_name} to course {course_name}")
        pdf_bytes = uploaded_file.read()
        # 将二进制数据转换为 BytesIO 对象
        pdf_stream = BytesIO(pdf_bytes)
        # 使用 fitz 打开 PDF
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        toc = doc.get_toc() 
        ori_data = extract_toc_content(doc, toc)
        embedding_data = embedding_text(self.emedding_model, ori_data)

        # 生成cypher
        cyphers = generate_cypher(course_name, file_name, embedding_data)

        for cypher in tqdm(cyphers):
            try:
                self.kg.query(cypher)
            except Exception as e:
                print(f"Error: {e}")

        doc.close()

        print(f"Upload {file_name} to course {course_name}")
        return True
    
    
