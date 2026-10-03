from typing import Literal

from pydantic import BaseModel


class AgentRequest(BaseModel):
    intent: Literal["information", "email"]
    movie: str | None = None
    query: str
    recipient: str | None = None