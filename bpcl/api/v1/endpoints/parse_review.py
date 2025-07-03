from fastapi.routing import APIRouter
from bpcl.langgraph.agents.compliance_agent import ComplianceAgent
from bpcl.db.data_models.Bid import Bid
from bpcl.db.data_models.Review import (
    Review,
    ReviewSet,
    ReviewSetResponse,
    ReviewResponse,
    UpdateReview,
)
from bpcl import LOGGER
from traceback import format_exc
from fastapi import HTTPException, Body
from datetime import datetime, timezone
from typing import Optional
from beanie.operators import Set
from bson import ObjectId

router = APIRouter(prefix="/review",tags=["Review"])


@router.post("/generate/{bid_id}")
async def parse_review(bid_id: str):
    try:
        bid = await Bid.get(bid_id)
        config = {
            "configurable": {
                "thread_id": 1,
                "project_id": bid.project_id,
                "bid_id": bid.id,
            }
        }
        result = await ComplianceAgent.compliance_agent({"messages": []}, config=config)
        review_set = ReviewSet(
            application_id=bid.id,
            # review_set_id=result.review_set_id,
            score=result.score,
            feedback=result.feedback,
        )
        await review_set.insert()
        buffer = []
        for review in result.reviewSets:
            review_obj = Review(
                type=review.alert,
                reason=review.message,
                review_set_id=review_set.id,
                status="pending",
                title=review.title
                # score=review.score,
                # feedback=review.feedback
            )
            await review_obj.insert()
            print(review_obj)
            buffer.append(
                ReviewResponse(
                    id=str(review_obj.id),
                    type=review_obj.type,
                    review_set_id=str(review_obj.review_set_id),
                    reason=review_obj.reason,
                    title=review_obj.title,
                    status=review_obj.status,
                )
            )

        return ReviewSetResponse(
            # id=str(review_set.id),
            reviews=buffer,
            application_id=bid_id,
            score=result.score,
            feedback=result.feedback,
        )
    except Exception as e:
        LOGGER.debug(format_exc())
        return HTTPException(status_code=500, detail="Internal Server Error")


@router.patch("/{review_id}")
async def update_review(review_id: str, data: UpdateReview = Body(...)):
    review = await Review.get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    # review.updated_at = datetime.now(timezone.utc)
    await review.update(
        Set(
            {
                getattr(Review, f): v
                for f, v in data.model_dump(exclude_unset=True).items()
            }
        )
    )
    review.review_set_id = str(review.review_set_id)
    review.id = str(review.id)
    return ReviewResponse(**review.model_dump(),exclude_unset=True)
