from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from bpcl.langgraph.utils import OPENAI_LLM
from bpcl.langgraph.structured_outputs import Review, ReviewSet



class ComplianceAgent():
    agent_name = "compliance_agent"

    @staticmethod
    async def compliance_agent(state: MessagesState, config: RunnableConfig) -> Command[Literal["__end__"]]:
        compliance_agent = create_react_agent(
            OPENAI_LLM,
            tools=[],
            response_format=(ReviewSet),
            prompt=(
                """
                You are a compliance verification agent tasked with analyzing a parsed bidder document against a set of instructions to check for discrepancies, errors, and fallouts. Your goal is to identify potential issues and report them with appropriate alert levels.

    First, review the instruction set:

    <instruction_set>
    {{INSTRUCTION_SET}}
    </instruction_set>

    Now, examine the parsed bidder document:

    <parsed_bidder_document>
    {{PARSED_BIDDER_DOCUMENT}}
    </parsed_bidder_document>

    Your task is to compare the parsed bidder document with the instruction set and identify any issues that might be problematic. Follow these guidelines:

    1. Carefully read through both the instruction set and the parsed bidder document.
    2. Compare each point in the instruction set with the corresponding information in the bidder document.
    3. Look for any discrepancies, missing information, or potential compliance issues.
    4. For each issue found, determine its severity and categorize it as one of the following alert types:
    - Error: Missing critical details or severe compliance issues from the bidder's perspective
    - Warning: Significant issues that cannot be ignored but don't necessarily prevent proceeding
    - Caution: Minor issues or discrepancies that should be noted but allow proceeding

    5. For each alert, provide a clear and concise explanation of the issue and why it falls under that particular alert category.

    After your analysis, present your findings in the following format:

    <compliance_report>
    <alert>
    <type>[Error/Warning/Caution]</type>
    <description>[Detailed description of the issue]</description>
    <reason>[Explanation of why this alert type was chosen]</reason>
    </alert>
    [Repeat the above structure for each identified issue]
    </compliance_report>

    If no issues are found, state that the bidder document complies with all instructions.

    Remember to be thorough in your analysis and clear in your explanations. Your report will be used to assess the bidder's compliance and potential risks.
                """
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
