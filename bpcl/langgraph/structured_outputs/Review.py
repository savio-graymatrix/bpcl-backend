from pydantic import BaseModel, Field   
from typing import List, Literal


class Review(BaseModel):
    alert: Literal["warning", "error", "caution"] = Field(description="The alert as per the 'compliance_agent'")
    title: str = Field(description="The title of the review")
    message: str = Field(description="The reason of the alert by the 'compliance_agent'")

class ReviewSet(BaseModel):
    reviewSets: List[Review] = Field(description="An array of reviews, each containing an alert, title and a message")
    #reasoning: str = Field(description="The weighted scoring and reasoning of the 'compliance_agent' for the scoring")
    score: int = Field(description="The score of the 'compliance_agent' for the bid which should strictly be between 0 and 100")
    feedback: str = Field(description="The short and concise feedback of the 'compliance_agent' for the bid")