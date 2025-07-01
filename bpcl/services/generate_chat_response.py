from uuid import uuid4
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from typing import Optional
from bpcl.langgraph.workflows import GRAPHS
import json

def serialise_ai_message_chunk(chunk): 
    if(isinstance(chunk, AIMessageChunk)):
        return chunk.content
    else:
        raise TypeError(
            f"Object of type {type(chunk).__name__} is not correctly formatted for serialisation"
        )

async def generate_chat_responses(message: str, checkpoint_id: Optional[str] = None):
    is_new_conversation = checkpoint_id is None
    
    if is_new_conversation:
        # Generate new checkpoint ID for first message in conversation
        new_checkpoint_id = str(uuid4())

        config = {
            "configurable": {
                "thread_id": new_checkpoint_id,
                "project_id": "68628d545384d01e747d6b79"
            }
        }
        
        # Initialize with first message
        events = GRAPHS['chatbot'].astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )
        
        # First send the checkpoint ID
        yield f"data: {{\"type\": \"checkpoint\", \"checkpoint_id\": \"{new_checkpoint_id}\"}}\n\n"
    else:
        config = {
            "configurable": {
                "thread_id": checkpoint_id
            }
        }
        # Continue existing conversation
        events = GRAPHS['chatbot'].astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )

    async for event in events:
        event_type = event["event"]
        
        if event_type == "on_chat_model_stream":
            chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
            # Escape single quotes and newlines for safe JSON parsing
            safe_content = chunk_content.replace("'", "\\'").replace("\n", "\\n")
            
            yield f"data: {{\"type\": \"content\", \"content\": \"{safe_content}\"}}\n\n"
            
        elif event_type == "on_chat_model_end":
            # Check if there are tool calls for search
            tool_calls = event["data"]["output"].tool_calls if hasattr(event["data"]["output"], "tool_calls") else []
            search_calls = [call for call in tool_calls if call["name"] == "tavily_search_results_json"]
            
            if search_calls:
                # Signal that a search is starting
                search_query = search_calls[0]["args"].get("query", "")
                # Escape quotes and special characters
                safe_query = search_query.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
                yield f"data: {{\"type\": \"search_start\", \"query\": \"{safe_query}\"}}\n\n"
                
        elif event_type == "on_tool_end" and event["name"] == "tavily_search_results_json":
            # Search completed - send results or error
            output = event["data"]["output"]
            
            # Check if output is a list 
            if isinstance(output, list):
                # Extract URLs from list of search results
                urls = []
                for item in output:
                    if isinstance(item, dict) and "url" in item:
                        urls.append(item["url"])
                
                # Convert URLs to JSON and yield them
                urls_json = json.dumps(urls)
                yield f"data: {{\"type\": \"search_results\", \"urls\": {urls_json}}}\n\n"
    
    # Send an end event
    yield f"data: {{\"type\": \"end\"}}\n\n"