from langchain_openai import ChatOpenAI
from langchain.agents import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os

load_dotenv("E:\\py_code\\course_assistant\\.env")

api_key = os.getenv("GLM_API_KEY")
endpoint = os.getenv("Chat_endpoint")
glm_model = os.getenv("GLM_MODEL")

llm = ChatOpenAI(
    temperature=0.95,
    model=glm_model,
    openai_api_key="36032750afe145b24f366387a48dc2c8.GnNnrbcLqgUBCA3t",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)


# define a tool
@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

@tool
def get_sum(a: float, b: float) -> float:
    """Returns the sum of two numbers."""
    return a + b
# test the tool
# get_word_length.invoke("abc")

tools = [get_word_length, get_sum]

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant, but don't know current events",
        ),
        # 加入对话的历史
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)
llm_with_tools = llm.bind_tools(tools)
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

from langchain_core.messages import AIMessage, HumanMessage

# 手动记录对话历史
chat_history = []

# 创建智能体执行的管道
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)
from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

input1 = "how many letters in the word educa?"
result = agent_executor.invoke({"input": input1, "chat_history": chat_history})
# 需要手动记录对话历史
chat_history.extend(
    [
        HumanMessage(content=input1),
        AIMessage(content=result["output"]),
    ]
)
agent_executor.invoke({"input": "is that a real word?", "chat_history": chat_history})