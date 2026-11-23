from pydantic import Field, BaseModel
from langchain_core.messages import BaseMessage, HumanMessage
from app.core.llm import get_llm
from app.core.state import AgentState 
from app.services.retriver import hybrid_retriver

# ret will add tomorrow am tired