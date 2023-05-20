from pydantic import BaseModel,Field
from typing import List

class HotwordInput(BaseModel):
    textData: str #= Field(..., example="Type any word you want", description="Use to detect hot word")
    appId: int #= #Field(..., example=1, description="app id ")
    sessionId: str #= Field(..., example="1212sw1ss11", description="session")
    campaignId: int #= Field(..., example=1, description="id of the campaign")

class CampaignInput(BaseModel):
    campaignId: int = Field(..., example=1, description="id of the campaign")
    hotwords: List[str]

