"""
dashboard_ui.dashboard

Helper functions for the Streamlit UI to handle filtering and statistics.
Separating logic from UI allows for robust testing.
"""

def filter_functions(functions, search_term=None, status="All", current_style="google"):
    """
    Filter a list of functions based on search term and validation status.

    Args:
        functions (list): List of function dicts from the parser.
        search_term (str): Text to search in function names.
        status (str): "All", "Needs Fix", or "OK".
        current_style (str): The active docstring style to check against.

    Returns:
        list: Filtered list of functions.
    """
    filtered = []
    
    # Pre-process search term
    term = search_term.lower().strip() if search_term else ""

    for fn in functions:
        # 1. Search Filter (Function Name)
        if term and term not in fn["name"].lower():
            continue

        # 2. Status Filter
        is_complete = _is_docstring_complete(fn, current_style)
        
        if status == "Needs Fix" and is_complete:
            continue
        if status == "OK" and not is_complete:
            continue
            
        filtered.append(fn)
        
    return filtered

def _is_docstring_complete(fn, style):
    """
    Determines if a function is considered 'OK' for the UI filters.
    """
    if not fn.get("has_docstring"):
        return False
    
    doc = fn.get("docstring", "").lower()
    
    # Simple heuristic checks for style presence
    if style == "google":
        return "args:" in doc or "returns:" in doc or "raises:" in doc
    elif style == "numpy":
        return "parameters" in doc and ("-" in doc)
    elif style == "rest":
        return ":param" in doc or ":return" in doc
        
    return True

def get_stats(parsed_files):
    """Calculate summary stats for the dashboard."""
    if not parsed_files:
        return 0, 0, 0
        
    total_files = len(parsed_files)
    total_funcs = sum(len(f["functions"]) for f in parsed_files)
    total_docs = sum(
        1 for f in parsed_files 
        for fn in f["functions"] 
        if fn.get("has_docstring")
    )
    
    return total_files, total_funcs, total_docs