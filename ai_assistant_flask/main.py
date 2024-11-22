import asyncio
from flask import Flask, jsonify, request
from flask_cors import *
from mysql import login_list
import os, sys, json
DEBUG = True

current_file_path = os.path.abspath(__file__)

parent_dir = os.path.dirname(current_file_path)

func_dir = os.path.join(os.path.dirname(parent_dir),"ai_assistant_func")
sys.path.append(func_dir)

from stream_agent import chat_with_user
from utils.knowledge_database import Neo4jUtils
from utils.file_utils import FileUtils

app = Flask(__name__) 
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# 配置文件上传保存的目录
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 限制上传文件大小（例如，最大为 16MB）
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'pdf'}

# 检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

    KGName = data['KGName']
    fileU = FileUtils()
    status = fileU.UploadPDFFile(KGName, file_names[0], open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb'))
    result = {
        "response": status
    }
    # 删除文件
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return result
    
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
    data_dict_list = [{"username": item[0], "password": item[1], "id": item[2]} for item in data]

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
    
    return "True" if flag else "False"
# 知识库问答
@app.route('/api/knowledge_qa', methods=['POST'])
def knowledge_qa():
    data = request.json
    course_name, user_input, history = data['course_name'], data['user_input'], data['history']
    chunks, response, _ = asyncio.run(chat_with_user(course_name=course_name, user_input=user_input, chat_history=history))
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
    N4J = Neo4jUtils()
    status = N4J.CreateCourse(Name)
    result = {
        "response": status
    }
    return result

# 获取所有知识库名称
@app.route('/api/get_knowledgename', methods=['GET'])
def get_knowledge():
    N4J = Neo4jUtils()
    result = N4J.FindAllClass()
    return jsonify(result)

# 获取知识库中的书籍名称
@app.route('/api/get_books', methods=['POST'])
def get_books():
    data = request.json
    KGName = data['KGName']
    N4J = Neo4jUtils()
    result = N4J.FindAllBook(KGName)
    return jsonify(result)

# 获取书籍中的所有Chunk
@app.route('/api/get_chunks', methods=['POST'])
def get_chunks():
    data = request.json
    Book_name = data['BookName']
    KGName = data['KGName']
    N4J = Neo4jUtils()
    result = N4J.FindAllChunk(Book_name)
    return jsonify(result)

# 修改某个chunk
@app.route('/api/modify_chunk', methods=['POST'])
def modify_chunk():
    data = request.json
    BookName = data['BookName']
    ChunkId = data['chunkSeqId']
    NewContent = data['content']
    N4J = Neo4jUtils()
    status = N4J.UpdateChunk(BookName, ChunkId, NewContent)
    result = {
        "response": status
    }
    return result

if __name__ == '__main__':

    app.run()
