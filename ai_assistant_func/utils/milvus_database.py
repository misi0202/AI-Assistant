import os, sys
from utils_base import BaseUtils
from dotenv import load_dotenv
from zhipuai import ZhipuAI
from pymilvus import (
    MilvusClient,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection, AnnSearchRequest, RRFRanker, connections,WeightedRanker
)
load_dotenv("/root/workspace/AI-Assistant/ai_assistant_func/.env")


class MilvusUtils(BaseUtils):
    def __init__(self) -> None:
        # 注册数据库连接
        self.client = MilvusClient(uri="http://localhost:19480")
        connections.connect(host="localhost", port="19480")
        self.CourseCollection = Collection(name="course_collection")
        self.ChunkCollection = Collection(name="Chunk_Collection")

        return super().__init__()
    
    def FindAllClass(self):
        """查询所有的课程 返回课程名称 list[str]"""

        # 查询集合中的所有数据
        results = self.CourseCollection.query(expr="",output_fields=["Course_name"], limit=1000)

        # 提取 Course_name 字段
        course_names = [result["Course_name"] for result in results]

        # 去重
        unique_course_names = list(set(course_names))

        return unique_course_names
    
    def FindAllBook(self, course_name: str):
        """根据课程名称 返回书籍名称 list[str]"""
        search_query = f"""
        MATCH (c:Course {{title: '{course_name}'}})-[:HAVE]->(b:Book) RETURN b.title
        """
        result = self.kg.query(search_query)
        res = []
        for r in result:
            res.append(r['b.title'])

        return res
    
    def FindAllChunk(self, book_title: str):
        """根据书籍名称 返回章节名称 list[dict]"""
        search_query = f"""
        MATCH (c:Chunk{{source_book: '{book_title}'}}) RETURN c.source_book as source, c.chunkSeqId as chunkSeqId,c.content as content
        """
        result = self.kg.query(search_query)

        return result
    
    def UpdateChunk(self, book_title: str, chunkSeqId: str, new_content: str):
        """根据书籍名称和SeqId 更新章节内容"""
        update_query = f"""
        MATCH (c:Chunk{{source_book: '{book_title}', chunkSeqId: '{chunkSeqId}'}})
        SET c.content = '{new_content}'
        """
        self.kg.query(update_query)
        # 更新embedding
        response = self.emedding_model.embeddings.create(
            model= self.embedding_name, 
            input=[new_content],
        )
        new_embedding = response.data[0].embedding
        update_query = f"""
        MATCH (c:Chunk{{source_book: '{book_title}', chunkSeqId: '{chunkSeqId}'}})
        WITH c, {new_embedding} as vector
        CALL db.create.setNodeVectorProperty(c, "textEmbedding", vector)
        """
        self.kg.query(update_query)
        return True
    
    def CreateCourse(self, course_name: str):
        """创建课程"""
        create_query = f"""
        MERGE (n:Course {{title: '{course_name}'}})
        ON MATCH SET n.title = n.title
        """
        self.kg.query(create_query)
        return True

if __name__ == "__main__":
    utils = MilvusUtils()
    result = utils.FindAllClass()
    for course in result:
        books = utils.FindAllBook(course)
        print(f"{course} has books: {books}")
        for book in books:
            chunks = utils.FindAllChunk(book)
            print(f"{book} has chunks: {chunks}")