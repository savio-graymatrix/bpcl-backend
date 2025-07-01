from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from bpcl.langgraph.agents.chatbot import ChatbotAgent
from langgraph.checkpoint.memory import MemorySaver


async def setup_chatbot_graph(checkpointer: Checkpointer = MemorySaver()) -> None:
    chatbot_graph_builder = StateGraph(MessagesState)
    chatbot_graph_builder.add_node(
        ChatbotAgent.agent_name, ChatbotAgent.chatbot, metadata={"node_type": ChatbotAgent.agent_name}
    )
    chatbot_graph_builder.add_edge(START, ChatbotAgent.agent_name)
    chatbot_graph_builder.add_edge(ChatbotAgent.agent_name, END)
    return chatbot_graph_builder.compile(
        checkpointer=checkpointer,
    )

    #
