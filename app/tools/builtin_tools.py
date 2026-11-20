import ast
import operator
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

_ddg = DuckDuckGoSearchRun()

_SAFE_OPS = {
    ast.Add : operator.add,
    ast.Sub : operator.sub,
    ast.Mult : operator.mul,
    ast.Div : operator.truediv,
    ast.Pow : operator.pow,
    ast.USub : operator.neg,
}

def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node.ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    return ValueError("Unsupported math expression")    

@tool
def web_search(query:str)-> str:
    """Search the web for current task event, live facts, or general information."""
    return _ddg.run(query)

@tool
def calculator(expression: str)-> str:
    """Safely Evaluatte a basic arithematic expression like for example '(25 * 4) + 10'"""
    try:
        tree = ast.parse(expression, mode='eval')
        result = _eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Calculation error {e}"
