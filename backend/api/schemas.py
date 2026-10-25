from typing import Dict, Optional

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    prediction: Optional[Dict] = None
