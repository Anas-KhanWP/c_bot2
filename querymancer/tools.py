from contextlib import contextmanager
from typing import Any, List
from functools import lru_cache
import json

from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.messages.tool import ToolCall
from langchain_core.tools import BaseTool
from pymongo import MongoClient

from querymancer.config import Config
from querymancer.logging import log, log_panel

def get_available_tools() -> List[BaseTool]:
    """Get a list of available tools."""
    return [
        list_collections,
        sample_collection,
        describe_collection,
        query_collection,
    ]
    
def call_tool(tool_call: ToolCall) -> Any:
    """Call a tool based on the tool call."""
    tools_by_name = {tool.name: tool for tool in get_available_tools()}
    tool = tools_by_name[tool_call["name"]]
    response = tool.invoke(tool_call["args"])
    return ToolMessage(content=response, tool_call_id=tool_call["id"])

@contextmanager
def with_mongo_client():
    client = MongoClient(Config.Database.MONGODB_URL)
    db = client[Config.Database.DATABASE_NAME]
    
    try:
        yield db
    finally:
        client.close()

@lru_cache(maxsize=1)
def _get_collections_cached():
    with with_mongo_client() as db:
        return db.list_collection_names()

@lru_cache(maxsize=100)
def _sample_collection_cached(collection_name: str, sample_size: int):
    with with_mongo_client() as db:
        collection = db[collection_name]
        documents = list(collection.find().limit(sample_size))
        return documents

@lru_cache(maxsize=50)
def _describe_collection_cached(collection_name: str):
    with with_mongo_client() as db:
        collection = db[collection_name]
        sample_doc = collection.find_one()
        count = collection.count_documents({})
        return sample_doc, count

@lru_cache(maxsize=200)
def _query_collection_cached(collection_name: str, query_json: str, limit: int):
    with with_mongo_client() as db:
        collection = db[collection_name]
        query_dict = json.loads(query_json) if query_json else {}
        
        log_panel(
            title="Executing Query",
            content=f"Collection: {collection_name}\nQuery: {query_dict}\nLimit: {limit}",
        )
        
        documents = list(collection.find(query_dict).limit(limit))
        
        log_panel(
            title="Query Result",
            content=f"Found {len(documents)} documents\nResults: {documents[:2] if documents else 'No results'}",
        )
        return documents
        
@tool(parse_docstring=True)
def list_collections(reasoning: str) -> str:
    """List all collections in the database.
    
    Args:
        reasoning: Explanation of why this tool is being used.
    """
    log_panel(
        title="List Collections Tool",
        content=f"Reasoning: {reasoning}",
    )
    try:
        collections = _get_collections_cached()
        return str(collections)
    except Exception as e:
        log(f"[red]Error listing collections: {str(e)}[/red]")
        return f"Error listing collections: {str(e)}"

@tool(parse_docstring=True)
def sample_collection(reasoning: str, collection_name: str, sample_size: int) -> str:
    """Sample documents from a specific collection.
    
    Args:
        reasoning: Explanation of why this tool is being used.
        collection_name: Name of the collection to sample from.
        sample_size: Number of documents to sample.
    """
    log_panel(
        title="Sample Collection Tool",
        content=f"Collection: {collection_name}\nSample Size: {sample_size}\nReasoning: {reasoning}",
    )
    try:
        documents = _sample_collection_cached(collection_name, sample_size)
        return "\n".join([str(doc) for doc in documents])
    except Exception as e:
        log(f"[red]Error sampling collection: {str(e)}[/red]")
        return f"Error sampling collection: {str(e)}"
    
@tool(parse_docstring=True)
def describe_collection(reasoning: str, collection_name: str) -> str:
    """Describe the structure of a collection by analyzing sample documents.
    
    Args:
        reasoning: Explanation of why this tool is being used.
        collection_name: Name of the collection to describe.
    """
    log_panel(
        title="Describe Collection Tool",
        content=f"Collection: {collection_name}\nReasoning: {reasoning}",
    )
    try:
        sample_doc, count = _describe_collection_cached(collection_name)
        if sample_doc:
            fields = list(sample_doc.keys())
            return f"Collection: {collection_name}\nDocument count: {count}\nSample fields: {fields}\nSample document: {sample_doc}"
        else:
            return f"Collection {collection_name} is empty"
    except Exception as e:
        log(f"[red]Error describing collection: {str(e)}[/red]")
        return f"Error describing collection: {str(e)}"
    
@tool(parse_docstring=True)
def query_collection(reasoning: str, collection_name: str, query_filter: dict = None, limit: int = 10) -> str:
    """Query a MongoDB collection with a find query.
    
    Args:
        reasoning: Explanation of why this tool is being used.
        collection_name: Name of the collection to query.
        query_filter: MongoDB query filter as a dictionary.
        limit: Maximum number of documents to return.
    """
    log_panel(
        title="Query Collection Tool",
        content=f"Collection: {collection_name}\nQuery: {query_filter}\nReasoning: {reasoning}",
    )
    
    try:
        query_json = json.dumps(query_filter) if query_filter else ""
        documents = _query_collection_cached(collection_name, query_json, limit)
        return "\n".join([str(doc) for doc in documents])
    except Exception as e:
        log(f"[red]Error querying collection: {str(e)}[/red]")
        return f"Error querying collection: {str(e)}"