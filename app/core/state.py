from typing import Any
from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """Agent's Shared State Can be acces accrossed by all nodes"""

    bot_id:str
    system_promtp:str
    provider:str
    model_override:str | None
    active_tools: dict[str, bool]
    db_uri: str | None

    route:str
    rewritten_query:str
    retrived_docs: list[dict[str, Any]]
    sql_query:str
    sql_result:str
    retry_count:int
    is_relevant:bool
    final_answer:str