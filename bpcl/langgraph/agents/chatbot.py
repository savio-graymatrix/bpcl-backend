from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langgraph.types import Command
from bpcl.langgraph.utils import OPENAI_LLM
from bpcl import LOGGER


class ChatbotAgent:
    agent_name = "chatbot_agent"

    @staticmethod
    async def chatbot(
        state: MessagesState, config: RunnableConfig
    ):
        
        chatbot_agent = create_react_agent(
            OPENAI_LLM,
            prompt=("""
            You are a chatbot assigned to answer the user queries.
            """),
            tools=[]
        )
        result = await chatbot_agent.ainvoke(state)
        LOGGER.debug(result)
        return Command(
            update={
                "messages": [
                    AIMessage(content=result["messages"][-1].content, name=ChatbotAgent.agent_name)
                ]
            },
            goto=END,
        )
