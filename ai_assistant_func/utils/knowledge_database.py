from langchain_community.graphs import Neo4jGraph
import os, sys
from utils_base import BaseUtils
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv("E:\\py_code\\course_assistant\\.env")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
embedding_key = os.getenv("EMBEDDING_KEY")
embedding_name = os.getenv("EMBEDDING_NAME")

class Neo4jUtils(BaseUtils):
    def __init__(self) -> None:
        # 注册数据库连接
        self.kg = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE)
        self.emedding_model = ZhipuAI(api_key = embedding_key)
        self.embedding_name = embedding_name
        return super().__init__()
    
    def FindAllClass(self):
        """查询所有的课程 返回课程名称 list[str]"""
        search_query = """
        MATCH (n:Course) RETURN DISTINCT n.title
        """
        result = self.kg.query(search_query)
        res = []
        for r in result:
            res.append(r['n.title'])

        return res
    
    def FindAllBook(self, course_name: str):
        """根据课程名称 返回书籍名称 list[str]"""
        search_query = f"""
        MATCH (c:Course {{title: '{course_name}'}})-[:HAVE]->(b:Book) RETURN b.title
        """
        result = self.kg.query(search_query)
        res = []
        for r in result:
            print(r['b.title'])
            if r['b.title']  == "NULL":
                continue
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
    utils = Neo4jUtils()
    result = utils.FindAllClass()
    for course in result:
        books = utils.FindAllBook(course)
        print(f"{course} has books: {books}")
        for book in books:
            chunks = utils.FindAllChunk(book)
            print(f"{book} has chunks: {chunks}")