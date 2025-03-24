import asyncio
from functools import wraps
import time
from flask import Flask, jsonify, request
from flask_cors import *
from mysql import login_list, update_user
import os, sys, json
DEBUG = True
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")

current_file_path = os.path.abspath(__file__)

parent_dir = os.path.dirname(current_file_path)

func_dir = os.path.join(os.path.dirname(parent_dir),"ai_assistant_func")
sys.path.append(func_dir)

from stream_agent import AgentUtils
# from utils.knowledge_database import Neo4jUtils
from utils.milvus_database import MilvusUtils
from utils.file_utils import FileUtils
from extract.extract_MinerU import handleFile
from extract.extract_PPTX import handlePPTFile
app = Flask(__name__) 
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# 配置文件上传保存的目录
UPLOAD_FOLDER = 'E:\\vue_pro\\ai_assistant\\ai_assistant_flask\\uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 限制上传文件大小（例如，最大为 16MB）
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'pptx', 'ppt'}

Milvus = MilvusUtils()
Agent = AgentUtils()
# 检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

# 上传至指定目录
@app.route('/api/upload', methods=['POST'])
def upload_file():
    print("Files received:", request.files.keys())
    for key in request.files:
        file = request.files[key]
        # 如果没有文件，返回错误
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 200
        
        # 如果文件合法，保存到指定目录
        if file and allowed_file(file.filename):
            # 确保上传目录存在
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            # 删除原有文件
            folder = Path(app.config['UPLOAD_FOLDER'])
            for f in folder.iterdir():
                if f.is_file():
                    f.unlink() 
                    print(f"已删除: {f}")
            
            # 保存文件
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return jsonify({'message': '文件上传成功', 'filename': filename}), 200
        else:
            return jsonify({'error': '不支持的文件类型'}), 200

# 将保存的文件上传至知识库
@app.route('/api/upload2kg', methods=['POST'])
def upload2kg():
    data = request.json
    file_names = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    # 默认只有一个文件
    filename = file_names[0]
    course_name = data['KGName']
    partition_name = Milvus.FindPartition(course_name)
    print(partition_name)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # 获取文件的后缀名 对PDF和PPT文件分别处理
    file_type = Path(file_path).suffix.lower()
    if file_type == ".pdf":
        status = handleFile(course_name, partition_name, file_path)
    elif file_type == ".pptx":
        status = handlePPTFile(course_name, partition_name, file_path)
    # 删除文件
    folder = Path(app.config['UPLOAD_FOLDER'])
    for file in folder.iterdir():
        if file.is_file():
            file.unlink() 
            print(f"已删除: {file}")
    return "succuss"
    
@app.route('/api/test', methods=['POST'])
def handle_ajax():

    data = request.json
    print(data)  # 打印传递的数据用于调试
    print(type(data))
    return "good"

# 用户管理获取
@app.route('/api/user_list', methods=['GET'])
def user_list():
    data = login_list()
    data_dict_list = [{"username": item[0], "password": item[1], "role": item[2], "id": item[3]} for item in data]

    # 转换为 JSON 格式
    json_data = json.dumps(data_dict_list, indent=4)
    return json_data
# 登录检查函数
@app.route('/api/login_check', methods=['POST'])
def login_check():
    data = request.json
    login_list_data = login_list()
    username, password = data['username'], data['passwd']
    flag = False
    for user in login_list_data:
        if user[0] == username and user[1] == password:
            flag = True
            data = {
            'username': user[0],
            'password': user[1],
            'role': user[2],
            'id': user[3]
            }
            user_data = jsonify(data)
            return "True" and user_data
        
    return "False"
# 知识库问答
@app.route('/api/knowledge_qa', methods=['POST'])
@time_it
def knowledge_qa():
    data = request.json
    course_name, user_input, history = data['course_name'], data['user_input'], data['history']
    for item in history:
        try:
            item["content"] = item["content"].split("\n\n---\n\n", 1)[0]
        except:
            pass
    chunks, response, _ = asyncio.run(Agent.chat_with_user(course_name=course_name, user_input=user_input, chat_history=history))
    result = {
        "chunks": chunks,
        "response": response
    }
    return result

# 创建知识库
@app.route('/api/create_knowledge', methods=['POST'])
def create_knowledge():
    data = request.json
    Name = data['KGName']
    PartitionName = data['PartitionName']
    status = Milvus.CreateCourse(Name, PartitionName)
    result = {
        "response": status
    }
    return result

# 获取所有知识库名称
@app.route('/api/get_knowledgename', methods=['GET'])
def get_knowledge():
    # N4J = Neo4jUtils()
    # result = N4J.FindAllClass()
    result = Milvus.FindAllClass()
    return jsonify(result)

# 获取知识库中的书籍名称
@app.route('/api/get_books', methods=['POST'])
def get_books():
    data = request.json
    KGName = data['KGName']
    # N4J = Neo4jUtils()
    # result = N4J.FindAllBook(KGName)
    result = Milvus.FindAllBook(KGName)
    return jsonify(result)

# 获取书籍中的所有Chunk
@app.route('/api/get_chunks', methods=['POST'])
def get_chunks():
    data = request.json
    Book_name = data['BookName']
    KGName = data['KGName']
    # N4J = Neo4jUtils()
    # result = N4J.FindAllChunk(Book_name)
    result = Milvus.FindAllChunk(Book_name)
    return jsonify(result)

# 修改某个chunk
@app.route('/api/modify_chunk', methods=['POST'])
def modify_chunk():
    data = request.json
    ChunkId = data['chunkSeqId']
    NewContent = data['content']
    # N4J = Neo4jUtils()
    # status = N4J.UpdateChunk(BookName, ChunkId, NewContent)
    status = Milvus.UpdateChunk(ChunkId, NewContent)
    result = {
        "response": status
    }
    return result

@app.route('/api/UpdateUser', methods=['POST'])
def UpdateUser():
    data = request.json
    print(data)
    username = data['username']
    password = data['password']
    user_id = data['user_id']
    role = data['role']
    status = update_user(username, password, user_id, role)
    result = {
        "response": status
    }
    return result

if __name__ == '__main__':

    app.run()
