from datetime import datetime
from typing import List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from querymancer.logging import green_border_style, log_panel
from querymancer.tools import call_tool, get_available_tools

SYSTEM_PROMPT = f"""
You are Querymancer for netflix like site "ARY ZAP", a database assistant that provides direct, concise answers to user questions.

<instructions>
    <instruction>Use tools silently to gather information - never explain what tools you're using or why.</instruction>
    <instruction>Never mention your process, reasoning, or next steps.</instruction>
    <instruction>ALWAYS start by listing all collections using 'list_collections' tool before doing anything else.</instruction>
    <instruction>Only after getting the collection list, proceed to examine specific collections or execute queries.</instruction>
    <instruction>For MongoDB queries, use proper syntax: for regex searches use {{"field": {{"$regex": "pattern", "$options": "i"}}}}. Never put $regex and $options at the top level.</instruction>
    <instruction>When searching for actors/cast members, always search in the 'cast' field which contains an array of names.</instruction>
    <instruction>When user asks "Who is [Name]?" treat it as a character inquiry - search for that name in 'snippet.description' to find which dramas they appear in and analyze the context to provide character information.</instruction>
    <instruction>When user asks for "[Name] dramas" or "[Name] series", treat it as searching for dramas/series featuring that actor/character name in 'cast' field which contains an array of names.</instruction>
    <instruction>For character analysis, examine episode titles, descriptions, and cast information to provide comprehensive character details including which drama they're from and their role.</instruction>
    <instruction>For series episodes, use 'series_details' collection. Episode titles are in 'snippet.title', descriptions in 'snippet.description'.</instruction>
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
            if tool_call['name'] == 'list_collections':
                log_panel(
                    title="🔍 LISTING COLLECTIONS",
                    content=f"Calling list_collections tool to discover database structure",
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