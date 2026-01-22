import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

def generate_docstring_content(fn: dict, api_key: str = None) -> dict:
    """Generate structured docstring content using LLM."""
    
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return {
            "summary": f"Placeholder summary for {fn['name']} (No API Key).",
            "args": {a["name"]: "Description needed" for a in fn.get("args", [])},
            "returns": "Return value description",
            "raises": {}
        }

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, api_key=key)

    prompt = f"""
    Analyze this Python function and return ONLY valid JSON.
    Function: {fn['name']}
    Args: {[a['name'] for a in fn.get('args', [])]}
    Returns: {fn.get('returns')}
    
    JSON Schema:
    {{
      "summary": "Imperative mood description (e.g. 'Calculate the sum')",
      "args": {{ "arg_name": "description" }},
      "returns": "description",
      "raises": {{ "ErrorName": "condition" }}
    }}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        # Ensure we only parse the JSON part
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        return json.loads(content)
    except Exception as e:
        return {
            "summary": f"Error generating docstring: {str(e)}",
            "args": {},
            "returns": "Unknown",
            "raises": {}
        }