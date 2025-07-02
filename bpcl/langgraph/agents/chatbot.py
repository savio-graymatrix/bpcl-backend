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
        project_id = config["configurable"]["project_id"]
        bid_id = config["configurable"]["bid_id"]
        
        instruction_set = await InstructionSet.find_one({"project_id": ObjectId(project_id)})
        
        if instruction_set:
            # Get all instructions for this instruction set
            instructions = await Instruction.find({"instruction_set_id": instruction_set.id}).to_list()
            #print(instructions.id)
            instruction_contents = [instruction.content for instruction in instructions]
        else:
            instruction_contents = []

        review_set = await ReviewSet.find_one({"application_id": ObjectId(bid_id)})
        
        if review_set:
            # Get all reviews for this review set
            reviews = await Review.find({"review_set_id": review_set.id}).to_list()
            #print(reviews.id)
            review_contents = [review.reason for review in reviews]
        else:
            review_contents = []

        chatbot_agent = create_react_agent(
            OPENAI_LLM,
            prompt="""
            You are an AI assistant in a tender and bid review system. Your role is to help users with queries based on a set of instructions and a bid document review. Follow these guidelines carefully:

1. First, familiarize yourself with the instruction set:
<instructions>
{{INSTRUCTIONS}}
</instructions>

2. Next, review the bid document analysis:
<bid_review>
{{BID_DOCUMENT}}
</bid_review>

3. When handling user queries, adhere to these guidelines:
   a. Always base your responses on the information provided in the instruction set and bid review.
   b. If a query falls outside the scope of the provided information, politely inform the user that you cannot answer that specific question.
   c. Maintain a professional and helpful tone throughout the interaction.
   d. If clarification is needed, ask the user for more details before providing an answer.

4. Format your responses as follows:
   a. Begin with a brief acknowledgment of the user's query.
   b. Provide your answer, clearly referencing relevant parts of the instruction set or bid review when applicable.
   c. If appropriate, offer additional context or suggest related information that might be helpful.

5. To address a user query, follow this procedure:
   a. Carefully read and understand the user's question.
   b. Identify relevant information from the instruction set and bid review.
   c. Formulate a clear and concise response based on this information.
   d. Double-check that your answer aligns with the provided instructions and bid review.
   e. Present your response to the user.
            """.format(
                INSTRUCTIONS="\n".join(instruction_contents),
                BID_DOCUMENT="\n".join(review_contents)
            ),
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
