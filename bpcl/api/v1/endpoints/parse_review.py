from fastapi.routing import APIRouter
from bpcl.langgraph.agents.compliance_agent import ComplianceAgent
from bpcl.db.data_models.Bid import Bid

router = APIRouter(prefix="/review")

@router.post("/{bid_id}")
async def parse_review(bid_id: str):
    bid = await Bid.get(bid_id)
    config = {
        "configurable": {
            "thread_id": 1,
            "project_id": bid.project_id,
            "bid_id": bid.id
        }
    }
    result = await ComplianceAgent.compliance_agent({"messages": []}, config=config)
    return result
