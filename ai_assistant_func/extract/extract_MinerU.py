import json
import re
import shutil
from sentence_transformers import SentenceTransformer, util
from zhipuai import ZhipuAI
from nltk.tokenize import sent_tokenize
from snownlp import SnowNLP

import tqdm
import numpy as np
from extract.parse_MinerU import pdf_parse_main
import os, sys
import magic_pdf.model as model_config 
model_config.__use_inside_model__ = True;
import nltk
# nltk.download('punkt_tab')

current_file_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_file_path)
grandpa_dir = os.path.dirname(parent_dir)
sys.path.append(grandpa_dir)


from vectorstore.milvus import Milvus
# nltk.download('punkt')
# 在保留标点符号的前提下，使用 SnowNLP 进行分句
def split_with_snownlp(text):
    # 使用 SnowNLP 的分句功能
    s = SnowNLP(text)
    # 手动加回标点符号
    sentences = []
    for sentence in s.sentences:
        match = re.search(r'[。！？]', text)
        if match:
            # 添加分句内容和标点符号
            sentences.append(sentence + match.group())
            # 截取剩余部分文本
            text = text[len(sentence) + len(match.group()):]
        else:
            sentences.append(sentence)
    return sentences

def split_text(titles, paragraphs, chunk_size=300, overlap_size=100):
    """
    分割文本段落为指定大小的文本块 可指定chunk_size和overlap_size 使用贪心思想 先向前再向后计算

    Args:
        paragraphs (List[str]): 段落列表
        chunk_size (int): 分割后的段落大小 Defaults to 300.
        overlap_size (int, optional): 段落之间重叠大小 Defaults to 100.

    Returns:
        List[str]: 分割后的文本块列表
    """
    sentences = paragraphs
    chunks = []
    chunk_title = []
    i = 0
    while i < len(sentences):
        chunk = sentences[i]
        title = titles[i]
        overlap = ''
        prev_len = 0
        prev = i - 1
        # 向前计算重叠部分
        while prev >= 0 and len(sentences[prev])+len(overlap) <= overlap_size:
            overlap = sentences[prev] + ' ' + overlap
            prev -= 1
        chunk = overlap+chunk
        next = i + 1
        # 向后计算当前chunk
        while next < len(sentences) and len(sentences[next])+len(chunk) <= chunk_size:
            chunk = chunk + ' ' + sentences[next]
            next += 1
        
        chunks.append(chunk)
        chunk_title.append(title)
        i = next
    return chunk_title, chunks

def concat_json(json_data, language='zh'):
    # 结果存放列表
    result_title, result_content = [], []

    # 用于保存d内容的临时变量
    current_title = "No title"
    current_content = []

    # 遍历数据
    for i in range(len(json_data)):
        item = json_data[i]
        current_content = item.get('text', '')
        # 如果是 text_level 为 1 的节点
        if item.get('text_level') == 1:
            # 更新标题 同时跳过该节点
            current_title = item.get('text', '')
        
        # 如果是 type 为 text 的节点，且在 text_level 为 1 的节点之间
        elif item.get('type') == 'text':
            # 使用分词工具 对长文本进行分割
            
            if language == 'zh':
                try:
                    sentences = split_with_snownlp(current_content)
                except:
                    sentences = sent_tokenize(current_content)
            elif language == 'en':
                sentences = sent_tokenize(current_content)
            
            for sentence in sentences:
                # 如果句子长度小于10则跳过
                if sentence.strip() == '' or len(sentence) < 5:
                    continue
                # 添加标题和内容
                result_title.append(current_title)
                result_content.append(sentence)


    
    return result_title, result_content

def add_Emedding2Chunk(chunks, model, model_name):
    """将List中的文本块转换为embedding List

    Args:
        chunks (List): 文本块列表
        embeddings (List): embedding列表

    Returns:
        List: 更新后的文本块列表
    """
    new_chunks = []
    for i, chunk in tqdm.tqdm(enumerate(chunks), desc="Processing chunks", ncols=100):
        # chunk[0]是标题，chunk[1]是内容 标题加内容转换为embedding
        content = chunk[0] + chunk[1]
        # 有两种类型 第一种是SentenceTransformer
        if isinstance(model, SentenceTransformer):
            embeddings = model.encode(content)
        if isinstance(model, ZhipuAI):
            embeddings = model.embeddings.create(model= model_name, input=content).data[0].embedding

        new_chunks.append(embeddings)

    return new_chunks

def handleFile(Course_name, partition_name, pdf_path):
    pdf_name = os.path.basename(pdf_path).split(".")[0]
    pdf_parse_main(pdf_path = pdf_path, parse_method="auto", is_json_md_dump=True, is_draw_visualization_bbox=False, output_dir="E:\\vue_pro\\ai_assistant\\ai_assistant_func\\output\\")
    json_path = f"E:\\vue_pro\\ai_assistant\\ai_assistant_func\\output\\{pdf_name}\\{pdf_name}_content_list.json"

    model_1 = SentenceTransformer("E:\\vue_pro\\ai_assistant\\ai_assistant_func\\model\\Conan")
    model_2 = ZhipuAI(api_key = "864eeb3324cb0bd34584e397a70caacf.jllKABCzmHYJPxfV") 

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # 删除该文件夹
    folder_path = f"E:\\vue_pro\\ai_assistant\\ai_assistant_func\\output\\{pdf_name}"
    result_title, result_content = concat_json(data)
    split_title, split_content = split_text(result_title, result_content)
    chunks = [[split_title[i], split_content[i]] for i in range(len(split_title))]
    vector_1 = add_Emedding2Chunk(chunks, model_1, "Conan")
    vector_2 = add_Emedding2Chunk(chunks, model_2, "embedding-3")
    vector_1 = [np.array(vec, dtype=np.float32) for vec in vector_1]
    vector_2 = [np.array(vec, dtype=np.float32) for vec in vector_2]

    Course_vector = model_1.encode(Course_name)

    vectorstore = Milvus()
    # 创建collection
    vectorstore.create_chunk_collection()
    vectorstore.create_course_collection()

    vectorstore.create_partition(partition_name)
    vectorstore.insert_data(partition_name, split_title, split_content, vector_1, vector_2, Course_name, pdf_name)
    vectorstore.insert_course_data(Course_name, partition_name, pdf_name, Course_vector)

    shutil.rmtree(os.path.join("E:\\vue_pro\\ai_assistant\\ai_assistant_func\\output\\", pdf_name))
    return True

if __name__ == '__main__':
    pdf_path = "./pdf/Machine_Learning1.pdf"
    # 创建分区 分区名只能有数字字母下划线
    partition_name = "Machine_Learning"
    # 课程名
    Course_name = "机器学习"
    pdf_name = os.path.basename(pdf_path).split(".")[0]
    
    pdf_parse_main(pdf_path = pdf_path, parse_method="auto", is_json_md_dump=True, is_draw_visualization_bbox=False, output_dir="..\\output\\")
    json_path = f"../output/{pdf_name}/{pdf_name}_content_list.json"

    model_1 = SentenceTransformer("../model/Conan")
    model_2 = ZhipuAI(api_key = "864eeb3324cb0bd34584e397a70caacf.jllKABCzmHYJPxfV") 

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    # 删除该文件夹
    folder_path = f"E:\\vue_pro\\ai_assistant\\ai_assistant_func\\output\\{pdf_name}"
    # shutil.rmtree(folder_path)

    result_title, result_content = concat_json(data)
    split_title, split_content = split_text(result_title, result_content)
    chunks = [[split_title[i], split_content[i]] for i in range(len(split_title))]
    vector_1 = add_Emedding2Chunk(chunks, model_1, "Conan")
    vector_2 = add_Emedding2Chunk(chunks, model_2, "embedding-3")
    vector_1 = [np.array(vec, dtype=np.float32) for vec in vector_1]
    vector_2 = [np.array(vec, dtype=np.float32) for vec in vector_2]

    Course_vector = model_1.encode(Course_name)

    vectorstore = Milvus()
    # 创建collection
    vectorstore.create_chunk_collection()
    vectorstore.create_course_collection()

    vectorstore.create_partition(partition_name)
    vectorstore.insert_data(partition_name, split_title, split_content, vector_1, vector_2, Course_name, pdf_name)
    vectorstore.insert_course_data(Course_name, partition_name, pdf_name, Course_vector)

    shutil.rmtree(os.path.join("..\\output", pdf_name))

