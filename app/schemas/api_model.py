from typing import Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The user's question or prompt")
    thread_id : str= Field(default="default_session", description="Conversation session ID for memory")
    bot_id : str = Field(default="default_bot", description="Identifier for the bot configuration")
    system_prompt : Optional[str] = Field(default = None, description="Optional custom system prompt override")
    provider: str = Field(default="groq", description="Optional custom system prompt override")
    model_override : Optional[str] = Field(default=None, description="Specific model name override")
    active_tool: list[str] = Field(default_factory=list, description="List of enabled tool names")
    db_uri: Optional[str] = Field(default=None, description="SQLAlchemy database URI for SQL queries")

class ChatResponse(BaseModel):
    thread_id : str
    route_taken : str
    final_answer : str
    sql_query : Optional[str] = None