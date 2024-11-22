from zhipuai import ZhipuAI

client = ZhipuAI(api_key="36032750afe145b24f366387a48dc2c8.GnNnrbcLqgUBCA3t") 
response = client.embeddings.create(
    model="embedding-3", #填写需要调用的模型编码
     input=[
        "美食非常美味，服务员也很友好。",
        "这部电影既刺激又令人兴奋。",
        "阅读书籍是扩展知识的好方法。"
    ],
)
data = response.data
