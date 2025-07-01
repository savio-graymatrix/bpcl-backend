from .chatbot_graph import setup_chatbot_graph
from .reviewer_graph import setup_review_graph
from .project_graph import setup_project_graph
from bpcl import LOGGER
import os

GRAPHS = dict()


async def setup_graphs():
    GRAPHS.update(
        {
            "reviewer": await setup_review_graph(),
            "chatbot": await setup_chatbot_graph(),
            "project": await setup_project_graph(),
        }
    )
    for key,graph in GRAPHS.items():
        os.makedirs(f"{os.getcwd()}/docs", exist_ok=True)
        os.makedirs(f"{os.getcwd()}/docs/images", exist_ok=True)
        graph.get_graph().draw_mermaid_png(
            output_file_path=f"docs/images/{key}.png"
        )
    LOGGER.info(
        f"Graphs initialized:\n{"\n".join([f"{key}:{graph}" for key,graph in GRAPHS.items()])}"
    )
