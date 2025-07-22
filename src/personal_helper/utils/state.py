from typing_extensions import Literal

from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class RouteRequest(BaseModel):
    step: Literal["answer", "browser", "programming"] = Field(
        description="Decide what is next step"
    )

class Helper(MessagesState):
    step: str