from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.core.state import AgentState
from app.services.db_connector import get_schema_summary, execute_readonly_sql

def sql_agent_node(state : AgentState) -> dict:
    """Generate a read-only SQL query from live schema, execute it, and retry once on error."""
    db_uri = state.get("db_uri")
    if not db_uri:
        return {"sql_qery":"",
                 "sql_result":"No SQL database connected",
                 "retry_count":0}

    query = state.get("rewritten_query") or state["messages"][-1].content
    schema =  get_schema_summary(db_uri=db_uri)
    # language model part 

    llm = get_llm(
        role="smart", 
        provider=state.get("provider"),
        model_override=state.get("model_override")
    )

    system_message = (
        "You are a senior SQL engineer. Write ONE valid, read-only SQL SELECT query for the schema below.\n"
        "Return ONLY the raw SQL query—no markdown fences, no explanation.\n\n"
        f"Database Schema:\n{schema}"
    )

    sql = (
        llm.invoke([SystemMessage(content=system_message),
                      HumanMessage(content=query)])
                      .content.strip()
                      .removeprefix("```sql")
                      .removeprefix("```")
                      .removesuffix("```")
                      .strip()
    )

    retries = 0 
    try: 
        result = execute_readonly_sql(db_uri, sql)
    except Exception as err:
        retries = 1
        fix_prompt = (
            f"Your previous SQL failed:\n{sql}\n\nError: {err}\n",
            "Fix the Query using only valid tables/columns from the schema. Return only raw SQL" 
        )
        sql = (
        llm.invoke([SystemMessage(content=system_message),
                      HumanMessage(content=fix_prompt)])
                      .content.strip()
                      .removeprefix("```sql")
                      .removeprefix("```")
                      .removesuffix("```")
                      .strip()
        )
        try:
            result = execute_readonly_sql(db_uri, sql)
        except Exception as second_err:
            result = f"SQL execution failed after retry:{second_err}"

    return {
        "sql_query" : sql,
        "sql_result" : result,
        "retry_count" : retries
    }

    
