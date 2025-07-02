from typing import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, END
from langchain_core.messages import AIMessage
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from bpcl.langgraph.utils import OPENAI_LLM
from bpcl.langgraph.structured_outputs import InstructionSet
from bpcl.db.data_models import Project
from bpcl.langgraph.tools.parser import extract_from_pdf
from bpcl.db.data_models import Project
from bpcl.langgraph.tools.parser import extract_from_pdf

class InstructionAgent:
    agent_name = "instruction_agent"

    @staticmethod
    async def instruction_agent(
        state: MessagesState, config: RunnableConfig
    ):

        project_id = config["configurable"]["project_id"]
        document = await Project.find_one({"_id": project_id})
        document = document.rf_proposal.url
        instruction_agent = create_react_agent(
            OPENAI_LLM,
            tools=[extract_from_pdf],
            response_format=(InstructionSet),
            prompt=(
                """
                You are an Instruction Creation agent tasked with creating a comprehensive set of instructions based on uploaded documents and project details. These instructions will be used by a compliance verification agent to compare received tenders against the instruction set you create. Your goal is to extract important details and create precise, accurate instructions that can be used for compliance checking.
    
    You will be provided with 1 input:
    
    <uploaded_documents>
    {UPLOADED_DOCUMENTS}
    </uploaded_documents>

    You have to use the tools to upload and parse the {UPLOADED_DOCUMENTS} and then analyze the text for creating instructions.
    
    
    
    Carefully analyze the uploaded documents and project details. Pay close attention to:
    1. Specific requirements and specifications
    2. Deadlines and timelines
    3. Quality standards
    4. Legal and regulatory requirements
    5. Technical specifications
    6. Budget constraints
    7. Evaluation criteria
    
    Extract all important details that you believe are necessary for compliance checking. Focus on quantifiable and verifiable aspects that can be easily compared against submitted tenders.
    
    Create your instruction set using the following format:
    <instruction_set>
    1. [Category Name]
       1.1. [Specific Instruction]
       1.2. [Specific Instruction]
       ...
    
    2. [Category Name]
       2.1. [Specific Instruction]
       2.2. [Specific Instruction]
       ...
    
    [Continue with additional categories as needed]
    </instruction_set>
    
    Ensure that your instructions are:
    - Precise and unambiguous
    - Directly related to compliance verification
    - Organized in a logical and easy-to-follow manner
    - Comprehensive, covering all aspects of the project requirements
    
    Before finalizing your instruction set, review it to ensure:
    1. All critical details from the uploaded documents and project details are included
    2. Instructions are clear and can be easily used for compliance checking
    3. There are no contradictions or inconsistencies in the instructions
    
    Once you have created the instruction set, provide a brief explanation of your approach and any key considerations you took into account when creating the instructions. This explanation should be included before the instruction set in your response.
    
    Output your final response in the following format:
    <response>
    <explanation>
    [Your explanation of the approach and key considerations]
    </explanation>
    
    <instruction_set>
    [Your created instruction set]
    </instruction_set>
    </response>
    """.format(
                    UPLOADED_DOCUMENTS=document
                )
            ),
        )

        result = await instruction_agent.ainvoke(state)
        # print(result)
        return result['structured_response']
