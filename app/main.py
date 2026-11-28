from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage

from app.core.graph import agent_graph
from app.schemas.api_model import ChatRequest, ChatResponse

#fast api object initilisation
app = FastAPI(title="Multi Agent Rag And SQl API", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status":"ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        config={"configurable":{"thread_id":payload.thread_id}}

        initial_state = {
            "messages" : [HumanMessage(content=payload.query)],
            "bot_id" : payload.bot_id,
            "system_prompt" : payload.system_prompt,
            "provider" : payload.provider,
            "model_override" : payload.model_override,
            "active_tools" : payload.active_tool,
            "db_uri" : payload.db_uri
        }
        #the above dict will pass inside the invoke agent graph
        result = await agent_graph.ainvoke(initial_state, config=config)

        return ChatResponse(
            thread_id= payload.thread_id,
            route_taken= result.get("route", "unknown"),
            final_answer = result.get("final_answer", "")
            sql_query=result.get("sql_query"),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
        

