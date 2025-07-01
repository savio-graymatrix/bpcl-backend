from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from bpcl.langgraph.utils import OPENAI_LLM
from bpcl.langgraph.structured_outputs import Review, ReviewSet
from bpcl.langgraph.tools.parser import extract_from_pdf
from bpcl.db.data_models import InstructionSet, Instruction
from bpcl.db.data_models import Bid
from bson import ObjectId


class ComplianceAgent():
    agent_name = "compliance_agent"

    @staticmethod
    async def compliance_agent(state: MessagesState, config: RunnableConfig) -> Command[Literal["__end__"]]:
        
        project_id = config["configurable"]["project_id"]
        bid_id = config["configurable"]["bid_id"]
        document = await Bid.find_one({"_id": bid_id})
        document = document.documents.url
        print(project_id)
        # Find the instruction set for this project
        instruction_set = await InstructionSet.find_one({"project_id": ObjectId(project_id)})
        print(instruction_set)
        # if not instruction_set:
        #     # If no instruction set found for project_id, try using project_id as instruction_set_id
        #     instruction_set = await InstructionSet.find_one({"_id": project_id})
            
        if instruction_set:
            # Get all instructions for this instruction set
            instructions = await Instruction.find({"instruction_set_id": instruction_set.id}).to_list()
            #print(instructions.id)
            instruction_contents = [instruction.content for instruction in instructions]
        else:
            instruction_contents = []
        
        compliance_agent = create_react_agent(
            OPENAI_LLM,
            tools=[extract_from_pdf],
            response_format=(ReviewSet),
            prompt=(
                """
                You are an efficient compliance reviewer agent. Your task is to check a bid document against a set of instructions and identify any problems or issues, highlighting them with appropriate alert levels.

First, you will receive the bid document:

<bid_document>
{BID_DOCUMENT}
</bid_document>

Next, you will receive the instruction set for comparison:

<instruction_set>
{INSTRUCTION_SET}
</instruction_set>

Compare the bid document with the instructions thoroughly and highlight any discrepancies or issues. Use the following alert levels to categorize your findings:

- Error: Missing critical details or severe compliance issues from the bidder's perspective
- Warning: Significant issues that cannot be ignored but don't necessarily prevent proceeding
- Caution: Minor issues or discrepancies that should be noted but allow proceeding

To assist in your review, you have access to 1 tool:
1. A parsing tool to parse the bid document

Use this tool as needed to ensure a comprehensive review.

Conduct a thorough comparison of the bid document against the instructions. For each issue you identify, provide:
1. The alert level (Error, Warning, or Caution)
2. A clear explanation of the issue
3. The relevant section or quote from the bid document
4. The corresponding instruction or requirement that was not met or requires attention

Present your findings in the following format:

<findings>
<issue>
<alert_level>[Error/Warning/Caution]</alert_level>
<explanation>[Detailed explanation of the issue]</explanation>
<bid_quote>[Relevant quote from the bid document]</bid_quote>
<instruction_reference>[Corresponding instruction or requirement]</instruction_reference>
</issue>
[Repeat for each issue found]
</findings>

After listing all issues, provide a brief summary of your review, including the total number of issues found for each alert level.

<summary>
[Brief summary of the review and total issues per alert level]
</summary>

Remember to be thorough and accurate in your review. Check every aspect of the bid document against the instructions, and ensure that you haven't missed any potential issues or discrepancies.
                """.format(
                    BID_DOCUMENT=document,
                    INSTRUCTION_SET=instruction_contents
                )
            ),
        )

        result = await compliance_agent.ainvoke(state)

        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content, name=ComplianceAgent.agent_name
                    )
                ]
            },
            goto=END,
        )
