import re
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

_ENGINE_CACHE: dict[str, Engine] = {}
#re.compile makes this a reusable regex object
_FORBIDEN_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRAND|REVOKE)\b", re.IGNORECASE,

) 

def get_db_engine(db_uri: str) -> Engine:
    """Create a cache a SQLAlchemi enigne with connection pooling"""

    if db_uri not in _ENGINE_CACHE:
        engine = create_engine(db_uri, pool_pre_ping=True)#creates  an engine with a stable poole connection if no pool is active 
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")) #executes teh db command
        _ENGINE_CACHE[db_uri] = engine
    return _ENGINE_CACHE[db_uri]

def get_schema_summary(db_uri: str)-> str:
    """Inspect all tables and columns so the SQL agent knows the exact schema."""
    engine = get_db_engine(db_uri)
    inspector = inspect(engine )
    lines = []

    for table_name in inspector.get_table_names():
        cols = [
            f"{col['name']} ({col['type']})" for col in inspector.get_columns(table_name)
        ]
        lines.append(f"Table `{table_name}`: {', '.join(cols)}")

    return "\n".join(lines) if lines else "No table found in this database"

def execute_readonly_sql(db_uri: str, query: str) -> str:
    """Validate that a SQL query is strictly read-only and return formatted rows."""
    cleaned = query.strip().rstrip(";") #-> right end strip

    if not cleaned.lower().startswith(("select","with")):
        raise ValueError("Security Blocked: only SELECT or WITH read quries are permited")
    if _FORBIDEN_SQL.search(cleaned):
        raise ValueError("Security Blocked: Modifying Sql Keywords are not allowed")

    engine = get_db_engine(db_uri)
    with engine.connect() as conn:
        result = conn.execute(text(cleaned))
        columns = list(result.keys()) #list of columns name form the query
        rows = result.fetchmany(50)

    if not rows:
        return "Query execute sucessfully but returned 0 rows"

    header = " | ".join(columns)
    body = "\n".join(" | ".join(str(val) for val in row) for row in rows)
    return f"{header}\n{'-' * len(header)}\n{body}"

