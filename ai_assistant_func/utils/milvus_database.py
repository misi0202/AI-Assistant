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
from sentence_transformers import SentenceTransformer, util
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(parent_dir), 'retriever'))
from vectorstore.milvus import Milvus


class MilvusUtils(BaseUtils):
    def __init__(self) -> None:
        # 注册数据库连接
        self.client = MilvusClient(uri="http://localhost:19480")
        connections.connect(host="localhost", port="19480")
        self.CourseCollection = Collection(name="course_collection")
        self.ChunkCollection = Collection(name="Chunk_Collection")
        self.vectorstore = Milvus()
        self.model_1 = SentenceTransformer("E:\\vue_pro\\ai_assistant\\ai_assistant_func\\model\\Conan")
        self.model_2 = ZhipuAI(api_key = "864eeb3324cb0bd34584e397a70caacf.jllKABCzmHYJPxfV")

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
        res = self.vectorstore.find_source(course_name)
        for r in res:
            if r == "NULL":
                res.remove(r)
        return res
    
    def FindAllChunk(self, book_title: str):
        """根据书籍名称 返回章节名称 list[dict]"""

        result = self.vectorstore.find_chunks(book_title)

        return result
    
    def UpdateChunk(self,  chunkSeqId: str, new_content: str):
        """根据书籍名称和SeqId 更新章节内容"""
        vector1 = self.model_1.encode(new_content)
        vector2 = self.model_2.embeddings.create(model= "embedding-3", input=new_content).data[0].embedding
        self.vectorstore.update_chunk( chunkSeqId, new_content, vector1, vector2)
        return True
    
    def CreateCourse(self, course_name: str, partition_name: str):
        """创建课程"""
        Course_vector = self.model_1.encode(course_name)
        self.vectorstore.create_partition(partition_name)
        self.vectorstore.insert_course_data(course_name, partition_name, "NULL", Course_vector)
        return True
    def FindPartition(self, course_name: str):
        """获取分区"""
        return self.vectorstore.find_partition(course_name)
    

if __name__ == "__main__":
    utils = MilvusUtils()
    result = utils.FindAllClass()
    for course in result:
        books = utils.FindAllBook(course)
        print(f"{course} has books: {books}")
        for book in books:
            chunks = utils.FindAllChunk(book)
            print(f"{book} has chunks: {chunks}")