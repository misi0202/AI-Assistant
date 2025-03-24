from sqlalchemy import create_engine
from sqlalchemy import text

HOSTNAME = 'localhost'
DATABASE = 'ai_assistant'
PORT = 3306
USERNAME = 'root'
PASSWORD = '123456'
DB_URL = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)
engine = create_engine(DB_URL)


def login_list():
    sql = 'select * from users'
    with engine.connect() as conn:
        results = conn.execute(text(sql))
        return [row for row in results]
    
def update_user(username, password, id, role):
    sql = 'UPDATE users SET username = :username, passwd = :password, role = :role WHERE id = :id'
    with engine.connect() as conn:
        conn.execute(text(sql), {
            'username': username,
            'password': password,
            'id': id,
            'role': role
        })
        conn.commit()  # 确保提交事务
    return "success"

if __name__ == '__main__':
    print(login_list())
