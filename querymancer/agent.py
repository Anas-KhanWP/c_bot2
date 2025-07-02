from datetime import datetime
from typing import List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from querymancer.logging import green_border_style, log_panel
from querymancer.tools import call_tool, get_available_tools

SYSTEM_PROMPT = f"""
You are Querymancer, a database assistant that provides direct, concise answers to user questions.

<instructions>
    <instruction>Use tools silently to gather information - never explain what tools you're using or why.</instruction>
    <instruction>Never mention your process, reasoning, or next steps.</instruction>
    <instruction>ALWAYS start by listing all tables using 'list_tables' tool before doing anything else.</instruction>
    <instruction>Only after getting the table list, proceed to examine specific tables or execute queries.</instruction>
    <instruction>Never show or mention SQL queries in your responses.</instruction>
    <instruction>Provide only the final answer that directly addresses the user's question.</instruction>
    <instruction>Format data clearly using tables or lists when appropriate.</instruction>
    <instruction>Be concise and direct - no explanatory text about your approach.</instruction>
    <instruction>DO NOT HIT ANY UPDATE OR DELETE COMMANDS!!!!</instruction>
    <instruction>DATABASE IS READONLY FOR YOU!!!!</instruction>
</instructions>

Today is {datetime.now().strftime("%Y-%m-%d")}
""".strip() 


def create_history() -> List[BaseMessage]:
    """Create an initial message history with a system prompt."""
    return [
        SystemMessage(content=SYSTEM_PROMPT),
    ]
    
def ask(
    query: str, history: List[BaseMessage], llm: BaseChatModel, max_iterations: int = 50
) -> str:
    log_panel(title="User Request", content=f"Query: {query}", style=green_border_style)
    
    n_iterations = 0
    messages = history.copy()
    messages.append(HumanMessage(content=f"{query}\n tables context: {get_available_tools()}"))
    
    while n_iterations < max_iterations:
        response = llm.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            return response.content
        for tool_call in response.tool_calls:
            if tool_call['name'] == 'list_tables':
                log_panel(
                    title="🔍 LISTING TABLES",
                    content=f"Calling list_tables tool to discover database structure",
                    style=green_border_style,
                )
            else:
                log_panel(
                    title="Tool Call",
                    content=f"Tool: {tool_call['name']}\nArguments: {tool_call['args']}",
                    style=green_border_style,
                )
            response = call_tool(tool_call)
            messages.append(response)
        n_iterations += 1
        
    raise RuntimeError(
        f"Maximum iterations ({max_iterations}) reached without a final response."
    )