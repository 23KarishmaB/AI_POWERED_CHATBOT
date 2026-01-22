"""
Tests for Milestone 4: Edge cases and UI helper logic.
"""
import pytest
from core.parser.python_parser import parse_path
import tempfile
import os

# 1. Edge Case: Empty File
def test_parse_empty_file():
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        pass # Create empty file
    
    try:
        # Should not crash
        results = parse_path(os.path.dirname(tmp.name))
        # Find our specific temp file result
        file_result = next((r for r in results if r['file_path'] == tmp.name), None)
        assert file_result is not None
        assert file_result['functions'] == []
    finally:
        os.remove(tmp.name)

# 2. Edge Case: Syntax Error in Source
def test_parse_syntax_error():
    with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as tmp:
        tmp.write("def broken_function(:\n    pass") # Syntax error
    
    try:
        # Parser should likely skip or handle gracefully (depending on implementation)
        # Assuming parser returns empty list for broken files or logs error
        results = parse_path(os.path.dirname(tmp.name))
        assert isinstance(results, list)
    finally:
        os.remove(tmp.name)

# 3. Edge Case: Class Methods (ensure they are captured)
def test_parse_class_methods():
    content = """
class MyClass:
    def method_one(self):
        pass
    """
    with tempfile.NamedTemporaryFile(suffix=".py", mode='w', delete=False) as tmp:
        tmp.write(content)
        
    try:
        results = parse_path(os.path.dirname(tmp.name))
        functions = [f for r in results for f in r['functions'] if r['file_path'] == tmp.name]
        
        names = [f['name'] for f in functions]
        assert "method_one" in names
    finally:
        os.remove(tmp.name)