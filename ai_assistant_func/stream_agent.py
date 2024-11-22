from dotenv import load_dotenv
import os, sys
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.graphs import Neo4jGraph
from langchain.tools import tool
from langchain_core.callbacks import Callbacks
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from zhipuai import ZhipuAI
import asyncio
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), 'retriever'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
load_dotenv("E:\\vue_pro\\ai_assistant\\ai_assistant_func\.env")

from retriever_base import BaseRetriever
from timer import time_it

GLM_MODEL = os.getenv("GLM_MODEL")
GLM_API_KEY = os.getenv("GLM_API_KEY")
GLM_ENDPOINT = os.getenv("GLM_ENDPOINT")
# print(GLM_MODEL, GLM_API_KEY, GLM_ENDPOINT)
model = ChatOpenAI(
    temperature=0.95,
    model=GLM_MODEL,
    openai_api_key=GLM_API_KEY,
    openai_api_base=GLM_ENDPOINT,
    streaming= True
)

@tool
async def RAG_retriever(query : str) -> list[dict]:
    """注册RAG的检索器工具 定义来自于retriever

    Returns:
        list[dict]: 检索到的知识和置信度
    """
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
    Retriever = BaseRetriever(database = kg, embedding_model = embedding_model, 
                              embedding_name = embedding_name, index_name = "chunk_index")
    result = Retriever.retrieve(query=query)

    return result

@tool
async def single_retriever(course_name: str, query : str) -> list[dict]:
    """注册单一课程的检索器工具 

    Returns:
        list[dict]: 检索到的知识和置信度
    """
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
    Retriever = BaseRetriever(database = kg, embedding_model = embedding_model, 
                              embedding_name = embedding_name, index_name = "chunk_index")
    result = Retriever.single_retrieve(course_name=course_name, query=query)

    return result

# 注册agent 构建模板
def init_agent():
    """初始化agent 创建提示词模板"""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are professor with rich knowledge about {course_name}. 
                Use single_retriever tool to get the knowledge and answer the question""",
            ),
            # 加入对话的历史
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )


    tools = [single_retriever]
    agent = create_openai_tools_agent(
        model.with_config({"tags": ["agent_llm"]}), tools, prompt
    )
    # 注意这里的run_name:Agent参数 
    agent_executor = AgentExecutor(agent=agent, tools=tools).with_config(
        {"run_name": "Agent"}
    )
    return agent_executor
# The output from .stream alternates between (action, observation) pairs, finally concluding with the answer if the agent achieved its objective.
# .stream方法的输出在(action, observation)对之间交替，最后以答案结束
# Actions: AgentAction及其子类 Observation: 代理迄今为止的操作历史，包括当前操作及其观察结果、包含函数调用结果（又称观察结果）的聊天信息
async def chat_with_user(course_name = "Machine Learning", user_input = "What is Lasso Regression?", chat_history = []):
    agent_executor = init_agent()
    chunks = []
    async for step in agent_executor.astream(
    {"course_name": course_name,"input": user_input, "chat_history": chat_history}):
        if "steps" in step:
            for step in step["steps"]:
                chunks = step.observation
        elif "output" in step:
            result = step["output"]
            chat_history.extend([HumanMessage(content=user_input),AIMessage(content=result)])

    return chunks, result, chat_history



async def test():
    agent_executor = init_agent()
    chat_history = []
    course_name = "Machine Learning"
    user_input = "What is Lasso Regression?"
    async for step in agent_executor.astream(
    {"course_name": course_name,"input": user_input, "chat_history": chat_history}
    ):
        # Agent Action
        if "actions" in step:
            for action in step["actions"]:
                print(f"Calling Tool: `{action.tool}` with input `{action.tool_input}`")
        # Observation
        elif "steps" in step:
            for step in step["steps"]:
                print(f"Tool Result: `{step.observation}`")
        # Final result
        elif "output" in step:
            print(f'Final Output: {step["output"]}')
            chat_history.extend([HumanMessage(content=user_input),AIMessage(content=step["output"])])
        else:
            raise ValueError()
        print("---")

# 每次动作包括一个AgentAction（actions和messages）和一个Observation(messages和steps)
if __name__ == "__main__":
    # 测试
    # asyncio.run(test())
    chat_history = []
    while True:
        user_input = input(f"\033[33m请输入你的问题：\033[0m\n")
        # What is Lasso Regression? What is the Ridge Regression and the difference between Lasso and Ridge Regression?
        chunks, result, chat_history = asyncio.run(chat_with_user(user_input=user_input, chat_history=chat_history))
        print(f"\033[32m检索结果:\033[0m\n")
        print(f"{chunks}")
        print(f"\033[34m回答:\033[0m\n{result}")



# 如果不适合astream 可以改为astrean.events这个函数 参考https://python.langchain.com/v0.1/docs/modules/agents/how_to/streaming/#custom-streaming-with-events