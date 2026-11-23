from langchain_core.tools import BaseTool
from app.tools.builtin_tools import web_search, calculator
from app.tools.custom_tools import CUSTOM_TOOLS

TOOL_CATALOG: dict[str, BaseTool]={
    "web_search" : web_search,
    "calculator" : calculator,
    **{tool.name : tool for tool in CUSTOM_TOOLS}
    
}

def get_active_tools(active_flag: dict[str: bool] | None) -> list[BaseTool]:
    """returns only the tool which is currenlty toggled ON for this session."""
    if not active_flag:
        return []

    return [tool_obj 
            for name, tool_obj in TOOL_CATALOG.items() 
            if active_flag.get(name, False)]

def list_available_tools()-> list[dict[str, str]]:
    """Return tool name and description so the UI can auto-generate toogle switches"""
    return [{'name': name, 'description': tool_obj} 
            for name, tool_obj in TOOL_CATALOG.items()]
  