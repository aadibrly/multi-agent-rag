from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage
from app.core.llm import get_llm
from app.core.state import AgentState

class RouteDecision(BaseModel):
    route: str= Field(
        description="One of: 'rag', 'sql', 'tools', 'direct'"
    )
    rewritten_query: str= Field(
        description= "Standalone, unambigious search/SQL query resolved from chat history"

    )

def router_node(state: AgentState) -> dict:
    llm = get_llm(tire='fast').with_structured_output(RouteDecision)
    enabled = set(state.get("enabled_tools") or [])
    has_db = bool(state.get()) 