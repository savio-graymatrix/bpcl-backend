from fastapi.routing import APIRouter
from bpcl.langgraph.agents.compliance_agent import ComplianceAgent
from bpcl.db.data_models.Bid import Bid
from bpcl.db.data_models.Review import Review, ReviewSet
from bpcl import LOGGER
from traceback import format_exc
from fastapi import HTTPException

router = APIRouter(prefix="/review")

@router.post("/{bid_id}")
async def parse_review(bid_id: str):
    try:
        bid = await Bid.get(bid_id)
        config = {
            "configurable": {
                "thread_id": 1,
                "project_id": bid.project_id,
                "bid_id": bid.id
            }
        }
        result = await ComplianceAgent.compliance_agent({"messages": []}, config=config)
        review_set = ReviewSet(
            application_id=bid.id,
            #review_set_id=result.review_set_id,
            score=result.score,
            feedback=result.feedback
        )
        await review_set.insert()

        for review in result.reviewSets:
            review_obj = Review(
                type=review.alert,
                reason=review.message,
                review_set_id=review_set.id,
                status="pending"
                #score=review.score,
                #feedback=review.feedback
            )
            await review_obj.insert()
        
        return result
    except Exception as e:
        LOGGER.debug(format_exc())
        return HTTPException(status_code=500, detail="Internal Server Error")

