from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.core.state import AgentState

def synthesizer_agent_node(state: AgentState) -> dict:
    """Synthesize the final natural-language response from RAG or SQL outputs."""
    query = state.get("rewritten_query") or state["messages"][-1].content
    route = state.get("route", "rag")

    retrived_docs = state.get("retrived_docs", [])
    sql_query = state.get("sql_query", "")
    sql_result = state.get("sql_result", "")

    llm = get_llm(role="smart",
                  provider=state.get("provider"),
                  model_override=state.get("model_override"),
                  )

    if route == "sql":
        context_block = (
            f"Executed SQL query:\n{sql_query}\n\n"
            f"Database Result:\n{sql_result}\n"
            )
        system_msg = (
            "You are a helpful data analyst assistant. Answer the user's question "
            "clearly and concisely using ONLY the provided SQL query results. "
            "Do not invent numbers or mention internal database errors unless no data was returned."
        )
    else:
        formatted_doc = f"\n\n--\n\n".join(
            doc['content'] for doc in retrived_docs
        ) if retrived_docs else "No relevent document found"

        context_block = f"Retrived Knowledge Base Context:\n{formatted_doc}"
        system_msg = (
            "You are a helpful knowledge assistant. Answer the user's question "
            "accurately using ONLY the provided context. If the context does not "
            "contain the answer, state that clearly instead of guessing."
        )


    human_prompt = f"User prompt:{query}\n\n{context_block}"
    response = llm.invoke(
        [SystemMessage(content=system_msg),
         HumanMessage(content=human_prompt)]
    )

    return{
        "messages": [AIMessage(content=response.content)],
        "final_answer" : response.content
    }
      