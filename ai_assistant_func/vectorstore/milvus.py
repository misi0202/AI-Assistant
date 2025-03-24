import random
import string
import numpy as np

from pymilvus import (
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection, AnnSearchRequest, RRFRanker, connections,MilvusClient
)

class Milvus():

    def __init__(self, 
                host = "localhost",
                port = "19480",
                col_name = "Chunk_Collection"):
        self.host = host
        self.port = port
        self.col_name = col_name
        connections.connect(host=self.host, port=self.port)
        self.client = MilvusClient(
        uri="http://localhost:19480"
        )
    
    # 为Chunk创建分区
    def create_partition(self, partition_name):
        self.client.create_partition(
        collection_name="Chunk_Collection",
        partition_name=partition_name
        )

    # 创建Chunk Collection
    def create_chunk_collection(self,dim_1=1792, dim_2 = 2048, drop = False):
        fields = [
                    FieldSchema(name="chunkSeqId", dtype=DataType.VARCHAR,is_primary=True, auto_id=True, max_length=100),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="source_book", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="course_name", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="vector1", dtype=DataType.FLOAT_VECTOR,dim=dim_1),
                    FieldSchema(name="vector2", dtype=DataType.FLOAT_VECTOR,dim=dim_2),
                    FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=65535), 
                    FieldSchema(name="partition_name", dtype=DataType.VARCHAR, max_length=65535)
                    ]
        schema = CollectionSchema(fields, "")
        check_collection = utility.has_collection(self.col_name)
        if check_collection and drop:
            drop_result = utility.drop_collection(self.col_name)

        self.col = Collection(self.col_name, schema, consistency_level="Strong", auto_id=True)

        # 创建索引
        index = {"index_type": "IVF_FLAT","metric_type": "L2","params": {"nlist": 128}}
        self.col.create_index("vector1", index)
        self.col.create_index("vector2", index)
        self.col.load()
    # 创建Course Collection
    def create_course_collection(self, dim=1792):
        # 定义字段
        course_name_field = FieldSchema(name="Course_name", dtype=DataType.VARCHAR, max_length=100)
        partition_name_field = FieldSchema(name="partition_name", dtype=DataType.VARCHAR, max_length=100)
        source_name_field = FieldSchema(name="source_name", dtype=DataType.VARCHAR, max_length=500, is_primary=True)
        course_vector_field = FieldSchema(name="Course_vector", dtype=DataType.FLOAT_VECTOR,dim=dim)

        schema = CollectionSchema(fields=[course_name_field, partition_name_field, source_name_field, course_vector_field],
                                description="存储课程、来源、分区名称的集合")   
        # 创建集合
        collection_name = "course_collection"
        collection = Collection(name=collection_name, schema=schema)

        index = {"index_type": "IVF_FLAT","metric_type": "L2","params": {"nlist": 128}}
        collection.create_index("Course_vector", index)
        collection.load()

    

        return 

        
    # 向Chunk Collections中插入数据
    def insert_data(self, partition_name, titles, chunks, vectors1, vectors2, course_name, source_book, ):

        num = len(chunks)
        data = [{"text": chunk, "source_book": source_book, "course_name": course_name,"vector1": vec1, "vector2": vec2, "title": t, "partition_name":partition_name} for chunk, vec1, vec2, t in zip(chunks, vectors1, vectors2, titles)]
        
        print(f"共计向数据库中插入{num}条")
        res = self.client.insert(
            collection_name=self.col_name,
            data=data,
            partition_name= partition_name
        )
        print(f"已全部插入")
        return True
    # 向Course Collection中插入数据
    def insert_course_data(self, course_name, partition_name, source_name, course_vector):
        data = [{"Course_name": course_name, "partition_name": partition_name, "source_name": source_name, "Course_vector": course_vector}]
        res = self.client.insert(
            collection_name="course_collection",
            data=data
        )
        print(f"已插入{course_name}数据")
        return True
    def find_partition(self, course_name):
        # 执行查询
        query_results = self.client.query(
        collection_name="course_collection",
        filter=f'Course_name == "{course_name}"',  # 构造过滤表达式
        output_fields=["partition_name"]                # 指定返回的字段
        )

        # 提取 source_name 并转换为列表
        partition_name = query_results[0]["partition_name"]
        return partition_name
    def find_source(self,Course_name):
        # 执行查询
        query_results = self.client.query(
        collection_name="course_collection",
        filter=f'Course_name == "{Course_name}"',  # 构造过滤表达式
        output_fields=["source_name"]                # 指定返回的字段
        )

        # 提取 source_name 并转换为列表
        source_list = [result["source_name"] for result in query_results]
        return source_list

    def find_chunks(self, book_title):
        # 执行查询
        query_results = self.client.query(
        collection_name=self.col_name,
        filter=f'source_book == "{book_title}"',  # 构造过滤表达式
        output_fields=["chunkSeqId", "text", "title"]                # 指定返回的字段
        )

        # 提取 source_name 并转换为列表
        result = [{"chunkSeqId": res["chunkSeqId"], "content": res["text"], "title": res["title"]} for res in query_results]
        return result
    
    def update_chunk(self, chunkSeqId, new_content, vector1, vector2):
        # 根据id查询内容
        query_results = self.client.query(
        collection_name=self.col_name,
        filter=f'chunkSeqId == "{chunkSeqId}"',  # 构造过滤表达式
        output_fields=["source_book","course_name", "title", "partition_name"]                # 指定返回的字段
        )
        source_book = query_results[0]["source_book"]
        course_name = query_results[0]["course_name"]
        title = query_results[0]["title"]
        partition_name = query_results[0]["partition_name"]
        # 删除旧数据
        self.client.delete(
        collection_name=self.col_name,
        filter = f"chunkSeqId == '{chunkSeqId}'"
        )
        # 重新插入

        data = {
            "chunkSeqId": chunkSeqId,
            "text": new_content,
            "source_book": source_book,
            "course_name": course_name,
            "vector1": vector1,
            "vector2": vector2,
            "title": title,
            "partition_name": partition_name
        }
        self.client.upsert(
        collection_name=self.col_name,
        data = data,
        partition_name = partition_name
        
        )
        return True