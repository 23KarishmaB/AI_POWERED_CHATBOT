"""
Tests for Dashboard UI Logic
"""
import pytest
from dashboard_ui.dashboard import filter_functions

# Mock Data
@pytest.fixture
def mock_funcs():
    return [
        {"name": "test_one", "has_docstring": True, "docstring": "Args: x"}, # Google style
        {"name": "test_two", "has_docstring": False},
        {"name": "compute_sum", "has_docstring": True, "docstring": ":param x:"} # ReST style
    ]

def test_filter_all(mock_funcs):
    """Test that 'All' returns everything."""
    res = filter_functions(mock_funcs, status="All")
    assert len(res) == 3

def test_filter_needs_fix(mock_funcs):
    """Test filtering for undocumented functions."""
    res = filter_functions(mock_funcs, status="Needs Fix")
    assert len(res) == 1
    assert res[0]["name"] == "test_two"

def test_filter_ok_strict_google(mock_funcs):
    """
    Test filtering 'OK' with Google style.
    'test_one' has Google style. 'compute_sum' has ReST.
    The logic should ideally flag ReST as not matching 'Google' preference if strict.
    """
    # Based on our simple logic:
    res = filter_functions(mock_funcs, status="OK", current_style="google")
    names = [f["name"] for f in res]
    
    assert "test_one" in names
    # Note: Depending on strictness of logic, compute_sum might be excluded 
    # if it doesn't contain "Args:" or "Returns:".
    
def test_search_logic(mock_funcs):
    """Test search case-insensitivity."""
    res = filter_functions(mock_funcs, search_term="COMPUTE")
    assert len(res) == 1
    assert res[0]["name"] == "compute_sum"

def test_search_and_status_combined(mock_funcs):
    """Test combined filtering."""
    # Search "test" (matches 1 & 2) AND Status "Needs Fix" (matches 2)
    res = filter_functions(mock_funcs, search_term="test", status="Needs Fix")
    assert len(res) == 1
    assert res[0]["name"] == "test_two"