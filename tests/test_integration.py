import pytest
import os
import shutil
from core.parser.python_parser import parse_path
from core.reporter.coverage_reporter import compute_coverage

# Setup dummy environment
TEST_DIR = "tests/temp_data"

@pytest.fixture
def setup_env():
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR)
    
    # Create a dummy python file
    with open(f"{TEST_DIR}/sample.py", "w") as f:
        f.write("""
def documented_function():
    '''This is a docstring.'''
    pass

def undocumented_function(x):
    return x * 2
""")
    yield
    shutil.rmtree(TEST_DIR)

def test_full_pipeline_coverage(setup_env):
    """Test parsing -> coverage calculation pipeline."""
    # 1. Parse
    parsed_files = parse_path(TEST_DIR)
    assert len(parsed_files) == 1
    assert len(parsed_files[0]["functions"]) == 2
    
    # 2. Check metadata
    funcs = {f["name"]: f for f in parsed_files[0]["functions"]}
    assert funcs["documented_function"]["has_docstring"] is True
    assert funcs["undocumented_function"]["has_docstring"] is False
    
    # 3. Compute Coverage
    report = compute_coverage(parsed_files)
    assert report["aggregate"]["total_functions"] == 2
    assert report["aggregate"]["documented"] == 1
    assert report["aggregate"]["coverage_percent"] == 50.0

def test_edge_case_empty_directory():
    """Ensure system handles empty folders gracefully."""
    os.makedirs("tests/empty_dir", exist_ok=True)
    parsed = parse_path("tests/empty_dir")
    assert parsed == []
    shutil.rmtree("tests/empty_dir")