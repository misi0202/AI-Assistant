import fitz  # PyMuPDF
import os
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from tqdm import *
import re


load_dotenv("E:\\py_code\\course_assistant\\.env")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
api_key = os.getenv("GLM_API_KEY")
endpoint = os.getenv("Chat_endpoint")
glm_model = os.getenv("GLM_MODEL")
embedding_key = os.getenv("EMBEDDING_KEY")
embedding_name = os.getenv("EMBEDDING_NAME")

def split_text(paragraphs, chunk_size=300, overlap_size=100):
    """
    分割文本段落为指定大小的文本块 可指定chunk_size和overlap_size 使用贪心思想 先向前再向后计算

    Args:
        paragraphs (List[str]): 段落列表
        chunk_size (int): 分割后的段落大小 Defaults to 300.
        overlap_size (int, optional): 段落之间重叠大小 Defaults to 100.

    Returns:
        List[str]: 分割后的文本块列表
    """
    sentences = [s.strip() for p in paragraphs for s in re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', p)]
    chunks = []
    i = 0
    while i < len(sentences):
        chunk = sentences[i]
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
        i = next
    return chunks


def extract_toc_content(doc, toc):
    """使用PyMuPDF提取目录中的内容

    Args:
        doc (Document): fitz读取的pdf内容
        toc : pdf目录信息

    Returns:
        List: 更新后的信息，每个条目包含一个列表，其中包含了原目录内容和当前章节的文本
    """
    
    updated_toc = []
    
    for i, item in enumerate(toc):
        level, title, start_page = item
        
        # 确定end_page，当前item的end_page是下一个item的start_page - 1
        if i + 1 < len(toc):
            end_page = toc[i + 1][2] - 1
        else:
            end_page = doc.page_count - 1  # 如果是最后一个条目，则end_page为最后一页
        
        # 提取start_page到end_page之间的文本
        contents = []
        for page_num in range(start_page - 1, end_page):  # 页码从0开始，所以要减1
            page = doc.load_page(page_num)
            # 按照文本块 分割并排序
            blocks = page.get_text("blocks")
            for block in blocks:
                block_text = block[4]
                # 去除空白字符
                cleaned_text = re.sub(r'\s+', '', block_text)
                if cleaned_text != "":
                    contents.append(block_text)

        # 将文本内容分割为合适大小的文本块、
        contents = split_text(contents)
        
        # 将合并后的文本内容添加到toc条目中
        updated_toc.append([level, title, start_page, contents])
    
    return updated_toc

def embedding_text(emedding_model, toc):
    """使用embedding模型将文本内容转换为向量"""

    print("embedding 执行中...")
    for item in tqdm(toc):
        texts = item[3]
        # 这里的texts是一个列表，包含了当前章节的所有文本内容
        results = []
        if len(texts) == 0:
            item.append(results)
            continue

        for _, text in enumerate(texts):

            response = emedding_model.embeddings.create(
            model= embedding_name, 
            input=[text],
            )
            results.append(response.data[0].embedding)
        item.append(results)

    return toc

        
def generate_cypher(course_name, book_title, toc):
    """根据课程名称、书名和目录信息生成Cypher生成语句"""
    book_title = f"'{book_title}'"
    course_name = f"'{course_name}'"
    cypher_queries = []
    parent_stack = []  # 用来存储不同级别的父节点
    # 创建该本书的父节点
    cypher_queries.append(f"CREATE (n:Book {{title:{book_title}}});")
    # 将其和课程节点连接
    cypher_queries.append(f"MATCH (c:Course {{title:{course_name}}}), (b:Book {{title:{book_title}}}) CREATE (c)-[:HAVE]->(b);")
    chunkSeqId = 0
    for item in toc:
        level, title, page_number, texts, emeddings = item
        node_name = f"'{title}'"

        # 如果等级为1 将其连接至book
        if level == 1:
            # 创建节点的 Cypher 语句 存放父亲属性
            create_node_query = f"CREATE (n:Chapter {{title: {node_name}, page: {page_number}, parent: {book_title}}});"
            cypher_queries.append(create_node_query)
            cypher_queries.append(f"MATCH (b:Book {{title:{book_title}}}), (c:Chapter {{title:{node_name}, parent:{book_title}}}) CREATE (b)-[:CONTAINS]->(c);")

        # 如果栈不为空，并且当前 level 小于栈顶 level，弹出栈顶元素，找到当前的父节点
        while parent_stack and parent_stack[-1]['level'] >= level:
            parent_stack.pop()

        # 如果栈中有父节点，则建立 PARENT 关系
        if parent_stack:
            parent_title = f"'{parent_stack[-1]['title']}'"
            # 创建节点 存放父亲属性
            create_node_query = f"CREATE (n:Chapter {{title: {node_name}, page: {page_number}, parent: {parent_title}}});"
            cypher_queries.append(create_node_query)

            parent_query = (f"MATCH (parent:Chapter {{title: {parent_title}}}), "
                            f"(child:Chapter {{title: {node_name}, parent: {parent_title}}}) "
                            f"CREATE (parent)-[:CHILD]->(child);")
            cypher_queries.append(parent_query)

        # 将当前节点压入栈中
        parent_stack.append({'level': level, 'title': title, 'page': page_number})

        # 分页创建节点的内容
        for text, embedding in zip(texts, emeddings):
            text = text.replace('\'','').replace('\"', '')
            cypher_queries.append(f"CREATE (n:Chunk {{content:'{text}', source_book:{book_title},chunkSeqId:'{chunkSeqId}', course_name:{course_name}}});")
            cypher_queries.append(f"MATCH (c:Chapter {{title:{node_name}}}), (ch:Chunk {{content:'{text}'}}) CREATE (c)-[:HAS_CHUNK]->(ch);")
            emedding_query = f"""
            MATCH (chunk:Chunk  {{content:'{text}', source_book:{book_title},chunkSeqId:'{chunkSeqId}'}}) 
            WITH chunk, {embedding} as vector
            CALL db.create.setNodeVectorProperty(chunk, "textEmbedding", vector)
            """
            cypher_queries.append(emedding_query)
            chunkSeqId += 1
    
    # 创建chunk之间的NEXT关系 根据chunkSeqId排序
    sort_query = f"""
    MATCH (from_same_section:Chunk)
    WHERE from_same_section.source_book = {book_title}
    WITH from_same_section
        ORDER BY from_same_section.chunkSeqId ASC
    WITH collect(from_same_section) as section_chunk_list
        CALL apoc.nodes.link(
            section_chunk_list, 
            "NEXT", 
            {{avoidDuplicates: true}}
        )  // NEW!!!
    RETURN size(section_chunk_list)
    """   
    cypher_queries.append(sort_query)
    # 创建chunk的索引 
    index_query = """
         CREATE VECTOR INDEX `chunk_index` IF NOT EXISTS
          FOR (c:Chunk) ON (c.textEmbedding) 
          OPTIONS { indexConfig: {
            `vector.dimensions`: 2048,
            `vector.similarity_function`: 'cosine'    
         }}
    """
    cypher_queries.append(index_query)
            

    return cypher_queries

if __name__ == "__main__":
    # 打开 PDF 文件
    # file_name = "E:\py_code\course_assistant\data\pdf\Scikit-Learn.TensorFlow.pdf"
    file_name = "E:\py_code\course_assistant\data\pdf\Machine Learning_ Step-by-Step Guide To Implement Machine Learning Algorithms with Python ( PDFDrive ).pdf"
    doc = fitz.open(file_name)
    book_title = os.path.basename(file_name)
    # 获取目录（书签）信息
    toc = doc.get_toc() 
    ori_data = extract_toc_content(doc, toc)
    emedding_model = ZhipuAI(api_key = embedding_key) 
    embedding_data = embedding_text(emedding_model, ori_data)

    kg = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE
    )
    # 删除所有节点和关系
    delete_query = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]-()
            DELETE n,r
            """
    kg.query(delete_query)
    # 模拟创建课程节点
    course_name = "机器学习"
    kg.query(f"CREATE (n:Course {{title: '{course_name}'}});")
    # 生成cypher
    cyphers = generate_cypher(course_name, book_title, embedding_data)
    print("query 执行中...")
    for cypher in tqdm(cyphers):
        try:
            kg.query(cypher)
        except Exception as e:
            print(f"Error: {e}")

    doc.close()
