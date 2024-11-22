import time
from functools import wraps

class BaseRetriever:
    def __init__(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

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

    
    def str2vector(self, query: str):
        response = self.embedding_model.embeddings.create(
            model= self.embedding_name, 
            input=[query],
            )
        result = response.data[0].embedding
        return result
    
    @time_it
    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """在neo4j中进行向量搜索

        Args:
            query (str): 需要搜索的问题
            top_k (int): 检索数量 Defaults to 3.

        Raises:
            NotImplementedError: _description_

        Returns:
            list[dict]: _description_
        """
        query_vector = self.str2vector(query)
        search_query = f"""
        WITH {query_vector} AS question_embedding
        CALL db.index.vector.queryNodes('{self.index_name}', {top_k}, question_embedding) yield node, score
        RETURN score, node.content AS content ,node.source_book AS source
        """
        try:
            response = self.database.query(search_query)
            return response
        except:
            raise NotImplementedError
        
    @time_it
    def single_retrieve(self, course_name: str, query: str, top_k: int = 3) -> list[dict]:
        """在neo4j中进行针对于某个课程的向量搜索

        Args:
            query (str): 需要搜索的问题
            top_k (int): 检索数量 Defaults to 3.

        Raises:
            NotImplementedError: _description_

        Returns:
            list[dict]: _description_
        """
        query_vector = self.str2vector(query)
        search_query = f"""
        WITH {query_vector} AS question_embedding
        CALL db.index.vector.queryNodes('{self.index_name}', {top_k}, question_embedding) yield node, score
        WHERE node.course_name = '{course_name}'
        RETURN score, node.content AS content ,node.source_book AS source
        """
        try:
            response = self.database.query(search_query)
            print(response)
            return response
        except:
            raise NotImplementedError

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from langchain_community.graphs import Neo4jGraph
    from zhipuai import ZhipuAI

    load_dotenv("E:\\py_code\\course_assistant\\.env")

    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
    kg = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE
    )
    embedding_key = os.getenv("EMBEDDING_KEY")
    embedding_name = os.getenv("EMBEDDING_NAME")
    embedding_model = ZhipuAI(api_key = embedding_key)
    Retriever = BaseRetriever(database = kg, embedding_model = embedding_model, embedding_name = embedding_name, index_name = "chunk_index")
    result = Retriever.retrieve(query="What is Lasso Regression?")
    print(result)
