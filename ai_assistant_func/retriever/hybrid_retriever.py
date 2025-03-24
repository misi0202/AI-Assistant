from functools import wraps
import time
from pymilvus import (
    MilvusClient,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection, AnnSearchRequest, RRFRanker, connections,WeightedRanker, RRFRanker
)

from langchain.tools import tool
from sentence_transformers import SentenceTransformer, util
from zhipuai import ZhipuAI

def Text2Vector(text, model, model_name):
    """文本转为向量

    Args:
        text: 文本
        model: 模型
        model_name: 模型名称

    Returns:
        vector: 输出向量
    """

    if isinstance(model, SentenceTransformer):
        embeddings = model.encode(text)
    if isinstance(model, ZhipuAI):
        embeddings = model.embeddings.create(model= model_name, input=text).data[0].embedding


    return embeddings

    # 计时器
def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)
        end_time = time.time()    # 记录结束时间
        elapsed_time = end_time - start_time  # 计算消耗时间
        print(f"Function '{func.__name__}' took {elapsed_time:.4f} seconds to execute.")
        return result
    return wrapper
    
@time_it
def hybrid_search(vector1, vector2, col_name, top_k = 3, partition_name=None, use_reranker = False):
    """RAG的混合检索器

    Args:
        vector1: 向量1
        vector2: 向量2
        col_name: 集合名称
        top_k: 检索数量
        partition_name: 分区名称

    Returns:
        
    """
    client = MilvusClient(uri="http://localhost:19480")
    connections.connect(host="localhost", port="19480")
    collection = Collection(name=col_name)
    if partition_name:
        print(f"加载分区 {partition_name}")
    else:
        collection.load()
    field_names = ["vector1", "vector2"]

    req_list = []
    nq = 1
    weights = [0.2, 0.3]
    default_limit = 5
    vectors_to_search = []

    search_param1 = {
        "data": vector1,
        "anns_field": field_names[0],
        "param": {"metric_type": "L2", "params": {"partition_name": partition_name}},
        "limit": 3,  

    }
    search_param2 = {
        "data": vector2,
        "anns_field": field_names[1],
        "param": {"metric_type": "L2", "params": {"partition_name": partition_name}},
        "limit": 3,
        }

    req = AnnSearchRequest(**search_param1)
    req_list.append(req)

    req = AnnSearchRequest(**search_param2)
    req_list.append(req)

    RRF_ranker = RRFRanker(k=60)
    # output_fields 用于指定返回结果中的字段，这里只返回文本字段
    # result = collection.hybrid_search(req_list, WeightedRanker(*weights), limit = top_k, partition_names = [partition_name],output_fields=['text', 'title', 'source_book'])
    # 考虑到两个向量并没有明显权重，故这里使用RRFRanker
    result = collection.hybrid_search(req_list, RRF_ranker, limit = top_k, partition_names = [partition_name],output_fields=['text', 'title', 'source_book'])
        
    similar_docs =  result[0]
    context = [{'content':doc.entity.get('title') + doc.entity.get('text'), 'source': doc.entity.get('source_book')} for doc in similar_docs]
    return context

def get_partition_name(Course_name, col_name='course_collection'):
    """获取分区名称

    Args:
        col_name: 集合名称
        Course_name: 课程名称

    Returns:
        partition_name: 分区名称
    """
    connections.connect(host="localhost", port="19480")
    
    # 加载指定的 collection
    collection = Collection(name=col_name)
    
    # 查询条件
    query = f"Course_name == '{Course_name}'"
    
    # 执行查询
    results = collection.query(expr=query, output_fields=["partition_name"])
    if not results:
        return None

    return results[0]['partition_name']


if __name__ == '__main__':
    # 测试
    import asyncio
    import numpy as np

    # async def test():
    #     text = "What is Ridge Regression?"
    #     col_name = "Chunk_Collection"
    #     # result = await hybrid_single_retriever(text, col_name)
    #     print(result)
        
    # asyncio.run(test())
    print(get_partition_name('机器学习'))