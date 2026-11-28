from pydantic import Field, BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.core.state import AgentState 
from app.services.retriver import hybrid_retriver

class GradeReslt(BaseModel):
    relevant : bool = Field(description="True if the retrived chunks contain usefull facts to answer the query else False")

def rag_agent_node(state: AgentState) -> dict:
    """Runs Hybrid retreval with NVIDIA reranking model. then safe-grade relevance"""

    sys_msg = "Judge whether the retrieved context helps answer the user's question."
    human_message = f"Question: {query}\n\nContent:\n{content_preview}"

    query = state.get("rewritten_query") or state["messages"]
    bot_id = state.get("bot_id", "default")

    chunks = hybrid_retriver(query=query, bot_id=bot_id, top_k=4)
    if not chunks:
        return {'retrived_docs':[], "is_relevant" : False }

    grader = get_llm(role='fast', provider=state.get("provider")).with_structured_output(GradeReslt)
    content_preview = "\n\n".join(c['content'] for c in chunks)
    grade: GradeReslt = grader.invoke([
        SystemMessage(content=sys_msg),
        HumanMessage(content=human_message)
        ])

    return {
        "retrived_docs" : chunks if grade.relevant else [],
        "is_relevant" : grade.relevant
}