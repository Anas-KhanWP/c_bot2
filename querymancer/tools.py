import sqlite3
from contextlib import contextmanager
from typing import Any, List

from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_core.tools import BaseTool

from querymancer.config import Config
from querymancer.logging import log, log_panel

def get_available_tools() -> List[BaseTool]:
    """Get a list of available tools."""
    return [
        list_tables,
        sample_table,
        describe_table,
        execute_sql,
    ]
    
def call_tool(tool_call: ToolCall) -> Any:
    """Call a tool based on the tool call."""
    tools_by_name = {tool.name: tool for tool in get_available_tools()}
    tool = tools_by_name[tool_call["name"]]
    response = tool.invoke(tool_call["args"])
    return ToolMessage(content=response, tool_call_id=tool_call["id"])

@contextmanager
def with_sql_cursor(readonly=True):
    conn = sqlite3.connect(Config.Paths.DATABASE_PATH)
    curr = conn.cursor()
    
    try:
        yield curr
        if not readonly:
            conn.commit()
    except Exception:
        if not readonly:
            conn.rollback()
        raise
    finally:
        curr.close()
        conn.close()
        
@tool(parse_docstring=True)
def list_tables(reasoning: str) -> str:
    """List all tables in the database.
    
    Args:
        reasoning: Explanation of why this tool is being used.
    """
    log_panel(
        title="List Tables Tool",
        content=f"Resoning: {reasoning}",
    )
    try:
        with with_sql_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [row[0] for row in cursor.fetchall()]
        return str(tables)
    except Exception as e:
        log(f"[red]Error listing tables: {str(e)}[/red]")
        return f"Error listing tables: {str(e)}"

@tool(parse_docstring=True)
def sample_table(reasoning: str, table_name: str, row_sample_size: int) -> str:
    """Sample rows from a specific table.
    
    Args:
        reasoning: Explanation of why this tool is being used.
        table_name: Name of the table to sample from.
        row_sample_size: Number of rows to sample.
    """
    log_panel(
        title="Sample Table Tool",
        content=f"Table: {table_name}\nRows: {row_sample_size}\nReasoning: {reasoning}",
    )
    try:
        with with_sql_cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {row_sample_size}")
            rows = cursor.fetchall()
        return "\n".join([str(row) for row in rows])
    except Exception as e:
        log(f"[red]Error sampling table: {str(e)}[/red]")
        return f"Error sampling table: {str(e)}"
    
@tool(parse_docstring=True)
def describe_table(reasoning: str, table_name: str) -> str:
    """Describe the structure of a table.
    
    Args:
        reasoning: Explanation of why this tool is being used.
        table_name: Name of the table to describe.
    """
    log_panel(
        title="Describe Table Tool",
        content=f"Table: {table_name}\nReasoning: {reasoning}",
    )
    try:
        with with_sql_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            rows = cursor.fetchall()
            
        return "\n".join(
            [str(row) for row in rows]
        )
    except Exception as e:
        log(f"[red]Error describing table: {str(e)}[/red]")
        return f"Error describing table: {str(e)}"
    
@tool(parse_docstring=True)
def execute_sql(reasoning: str, sql: str) -> str:
    """Execute a SQL query on the database.
    
    Args:
        reasoning: Explanation of why this tool is being used.
        sql: The SQL query to execute.
    """
    log_panel(
        title="Execute SQL Tool",
        content=f"SQL: {sql}\nReasoning: {reasoning}",
    )
    
    # Check for non-readonly operations
    sql_upper = sql.upper().strip()
    forbidden_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
    
    for keyword in forbidden_keywords:
        if sql_upper.startswith(keyword):
            return "I cannot assist with that"
    
    try:
        with with_sql_cursor(readonly=True) as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            return "\n".join([str(row) for row in rows])
    except Exception as e:
        log(f"[red]Error running Query: {str(e)}[/red]")
        return f"Error running query: {str(e)}"