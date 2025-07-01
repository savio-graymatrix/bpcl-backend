from langgraph.types import Checkpointer
from langgraph.graph import StateGraph, START, MessagesState, END
from bpcl.langgraph.agents.compliance_agent import ComplianceAgent
from langgraph.checkpoint.memory import MemorySaver

async def setup_review_graph(checkpointer: Checkpointer = MemorySaver()) -> None:

    global reviewgraph

    rgraph_builder = StateGraph(MessagesState)
    rgraph_builder.add_node(
        "reviewer", ComplianceAgent.compliance_agent, metadata={"node_type": "reviewer"}
    )
    rgraph_builder.add_edge(START, "reviewer")
    rgraph_builder.add_edge("reviewer", END)
    return rgraph_builder.compile(
        checkpointer=checkpointer,
    )
