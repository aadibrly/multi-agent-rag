from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llm import get_llm
from app.core.state import AgentState
from app.services.db_connector import get_schema_summary, execute_readonly_sql