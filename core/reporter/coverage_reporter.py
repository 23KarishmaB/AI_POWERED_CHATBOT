"""
core/reporter/coverage_reporter.py
Computes documentation coverage metrics from parsed AST data.
"""

import json
from typing import List, Dict, Any

def compute_coverage(parsed_files: List[Dict]) -> Dict[str, Any]:
    """
    Compute aggregate and per-file coverage stats.
    Returns dictionary with 'aggregate' and 'files' keys.
    """
    total_functions = 0
    documented_functions = 0
    file_stats = []

    # Handle empty input case gracefully
    if not parsed_files:
        return {
            "aggregate": {
                "total_functions": 0,
                "documented": 0,
                "coverage_percent": 0.0,
                "meets_threshold": False
            },
            "files": []
        }

    for file_data in parsed_files:
        funcs = file_data.get("functions", [])
        f_total = len(funcs)
        f_documented = sum(1 for f in funcs if f.get("has_docstring"))
        
        total_functions += f_total
        documented_functions += f_documented
        
        f_coverage = (f_documented / f_total * 100) if f_total > 0 else 0.0
        
        file_stats.append({
            "file_path": file_data.get("file_path", "unknown"),
            "total_functions": f_total,
            "documented": f_documented,
            "coverage_percent": round(f_coverage, 1)
        })

    # Global coverage
    coverage_percent = (documented_functions / total_functions * 100) if total_functions > 0 else 0.0

    return {
        "aggregate": {
            "total_functions": total_functions,
            "documented": documented_functions,
            "coverage_percent": round(coverage_percent, 1),
            "meets_threshold": coverage_percent >= 80
        },
        "files": file_stats
    }

def write_report(coverage_data: Dict, output_path: str):
    """Writes coverage data to a JSON file."""
    try:
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(coverage_data, f, indent=2)
    except Exception as e:
        print(f"Error writing report: {e}")