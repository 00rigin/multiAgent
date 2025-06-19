from pydantic import BaseModel, Field

class CalenderParams(BaseModel):
    title: str = Field(..., description="The title of the event")
    description: str = Field(..., description="The description of the event")
    start_at: str = Field(..., description="The start time of the event  (ISO 8601)")
    end_at: str = Field(..., description="The end time of the event  (ISO 8601)")


