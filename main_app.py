import json
import os
import difflib
import textwrap
import streamlit as st
from core.parser.python_parser import parse_path
from core.docstring_engine.generator import generate_docstring
from core.validator.validator import validate_docstrings, compute_complexity, compute_maintainability
from core.reporter.coverage_reporter import compute_coverage, write_report

# -------------------------------------------------
# 🎨 UI Configuration & CSS
# -------------------------------------------------
st.set_page_config(page_title="AI Code Reviewer", layout="wide", page_icon="🤖")

def inject_custom_css():
    st.markdown("""
        <style>
        /* 1. Use CSS Variables (var(--...)) so colors adapt to Light/Dark mode automatically. 
           2. No more hardcoded #FFFFFF or #000000 for main text.
        */
        
        .stApp {
            font-family: 'Inter', sans-serif;
        }

        /* CARD STYLING: Adapts to theme's secondary background color */
        .func-card {
            background-color: var(--secondary-background-color);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid var(--text-color); /* Subtle border for contrast */
            border-left: 5px solid #4B4B4B;
            transition: transform 0.2s;
            color: var(--text-color); /* Adaptive Text */
        }
        
        .func-card:hover {
            transform: scale(1.01);
            border-left: 5px solid #FF4B4B;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* METRIC CARDS: Force them to use theme colors */
        div[data-testid="stMetric"] {
            background-color: var(--secondary-background-color);
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: var(--text-color);
        }

        /* Metric Labels & Values: Inherit theme text color */
        div[data-testid="stMetricLabel"] {
            color: var(--text-color) !important;
        }
        div[data-testid="stMetricValue"] {
            color: var(--text-color) !important;
        }

        /* STATUS BADGES: Keep fixed colors but ensure text is readable */
        .badge-ok {
            background-color: #0df2c9;
            color: #000000 !important; /* Always black text on bright green */
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.8rem;
        }
        .badge-fix {
            background-color: #ff4b4b;
            color: #FFFFFF !important; /* Always white text on red */
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 0.8rem;
        }

        /* INPUT FIELDS: Ensure they respect theme */
        input, textarea {
            color: var(--text-color) !important;
            background-color: var(--secondary-background-color) !important;
        }
        
        /* Sidebar: Use native variables */
        section[data-testid="stSidebar"] {
            background-color: var(--secondary-background-color);
        }
        </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# 🧠 Logic Helpers
# -------------------------------------------------

def detect_docstring_style(docstring):
    """Detect if docstring follows Google, NumPy, or reST style."""
    if not docstring: return None
    doc_lower = docstring.lower()
    
    # Google
    if any(k in doc_lower for k in ['args:', 'returns:', 'raises:', 'yields:']): return 'google'
    
    # NumPy
    if ('parameters' in doc_lower and '----' in docstring) or \
       ('returns' in doc_lower and '----' in docstring): return 'numpy'
    
    # reST
    if ':param' in doc_lower or ':return' in doc_lower: return 'rest'
    
    return None

def is_docstring_complete(fn, style):
    """Check if function has a complete docstring in the specified style."""
    if not fn.get("has_docstring"): return False
    
    doc = fn.get("docstring", "")
    # Basic check for placeholder or empty content
    if len(doc.strip()) < 10 or "DESCRIPTION" in doc: return False
    
    # Style Check
    detected_style = detect_docstring_style(doc)
    if detected_style != style: return False
    
    return True

def apply_docstring(file_path, fn, generated_docstring):
    """
    Replace/Insert docstring with strict indentation control using textwrap.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 1. Calculate correct indentation (Parent Function + 4 spaces)
    def_indent = fn.get("indent", 0)
    indent_str = " " * (def_indent + 4) 
    
    # 2. Clean the generated docstring
    # Remove outer quotes if the AI added them
    clean_doc = generated_docstring.strip()
    if clean_doc.startswith('"""') or clean_doc.startswith("'''"):
        clean_doc = clean_doc[3:]
    if clean_doc.endswith('"""') or clean_doc.endswith("'''"):
        clean_doc = clean_doc[:-3]
    
    # 3. Normalize: Remove common leading whitespace (Dedent)
    # This prevents "double indentation" if the AI returned indented text
    clean_doc = textwrap.dedent(clean_doc).strip()
    
    # 4. Reconstruct with correct indentation
    # We start with the opening quotes
    final_lines = [f'{indent_str}"""\n']
    
    # Apply indentation to every line of the content
    for line in clean_doc.splitlines():
        if line.strip():
            final_lines.append(f"{indent_str}{line}\n")
        else:
            final_lines.append("\n") # Keep empty lines empty (no trailing spaces)
            
    # Closing quotes
    final_lines.append(f'{indent_str}"""\n')
    
    # 5. Insert into file
    insert_line = fn["start_line"]
    
    # NOTE: In a production app, we would use AST node replacement.
    # Here we simply insert at the start of the function body.
    # If a docstring exists, we insert BEFORE it (users can then delete the old one).
    lines[insert_line:insert_line] = final_lines

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def generate_diff(before, after):
    """Generate a unified diff string."""
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile="Original", tofile="Proposed", lineterm=""
    ))

# -------------------------------------------------
# 🚀 Application Layout
# -------------------------------------------------
inject_custom_css()

# Sidebar
with st.sidebar:
    st.title("🤖 AI Reviewer")
    st.markdown("---")
    menu = st.radio("Navigation", ["🏠 Dashboard", "📘 Docstring, Review & Fix", "📊 Analytics"], label_visibility="collapsed")
    
    st.markdown("---")
    st.subheader("⚙️ Settings")
    scan_path = st.text_input("Project Path", value="examples", help="Folder relative to root")
    
    if st.button("🚀 Scan Project", type="primary", use_container_width=True):
        if not os.path.exists(scan_path):
            st.error("Path not found!")
        else:
            with st.spinner("Analyzing AST & Metrics..."):
                parsed = parse_path(scan_path)
                cov = compute_coverage(parsed)
                st.session_state["parsed_files"] = parsed
                st.session_state["coverage"] = cov
                st.session_state["selected_file"] = None
                st.success("Scan Complete!")
                st.rerun()

# -------------------------------------------------
# 🏠 Dashboard View
# -------------------------------------------------
if menu == "🏠 Dashboard":
    st.title("Project Overview")
    
    if "coverage" in st.session_state:
        cov = st.session_state["coverage"]
        agg = cov.get("aggregate", {})
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Documentation Coverage", f"{agg.get('coverage_percent', 0)}%", delta_color="normal")
        c2.metric("Total Functions", agg.get("total_functions", 0))
        c3.metric("Documented", agg.get("documented", 0))
        c4.metric("Missing", agg.get("total_functions", 0) - agg.get("documented", 0))
        
        st.markdown("### 📌 Recent Activity")
        st.info("System ready. Go to 'Review & Fix' to start processing files.")
    else:
        st.warning("⚠️ No data found. Please run a scan from the sidebar.")

# -------------------------------------------------
# 📘 Review & Fix View
# -------------------------------------------------
elif menu == "📘 Review & Fix":
    st.title("📘 Code Review Studio")
    
    if "parsed_files" not in st.session_state:
        st.warning("Please scan the project first.")
    else:
        files = st.session_state["parsed_files"]
        
        # --- Toolbar ---
        t1, t2, t3 = st.columns([1, 2, 1])
        with t1:
            target_style = st.selectbox("Docstring Style", ["google", "numpy", "rest"])
        with t2:
            search_query = st.text_input("🔍 Search Function", placeholder="Type function name...")
        with t3:
            filter_status = st.selectbox("Filter", ["All", "Needs Fix", "OK"])

        st.markdown("---")

        # --- Layout: File List (Left) vs Editor (Right) ---
        col_list, col_editor = st.columns([1, 2])

        with col_list:
            st.subheader("📂 File Explorer")
            for f in files:
                fname = os.path.basename(f["file_path"])
                
                # Check file status
                functions = f.get("functions", [])
                needs_attn = any(not is_docstring_complete(fn, target_style) for fn in functions)
                
                # Apply Filters
                if filter_status == "Needs Fix" and not needs_attn: continue
                if filter_status == "OK" and needs_attn: continue

                # Card Rendering
                status_icon = "🔴" if needs_attn else "🟢"
                btn_label = f"{status_icon} {fname}"
                
                if st.button(btn_label, key=f"btn_{f['file_path']}", use_container_width=True):
                    st.session_state["selected_file"] = f["file_path"]

        with col_editor:
            sel_file = st.session_state.get("selected_file")
            
            if not sel_file:
                st.info("👈 Select a file to review suggestions.")
            else:
                # --- SAFE SEARCH: Handle case where file is not found (StopIteration fix) ---
                file_data = next((f for f in files if f["file_path"] == sel_file), None)
                
                if not file_data:
                    st.warning(f"⚠️ File not found in current scan: {os.path.basename(sel_file)}")
                    st.caption("Try re-scanning the project from the sidebar.")
                else:
                    st.subheader(f"Editing: `{os.path.basename(sel_file)}`")
                    
                    functions = file_data.get("functions", [])
                    
                    # Filter functions by search query
                    if search_query:
                        functions = [fn for fn in functions if search_query.lower() in fn["name"].lower()]

                    if not functions:
                        st.warning("No functions match criteria.")

                    for fn in functions:
                        is_complete = is_docstring_complete(fn, target_style)
                        
                        if filter_status == "Needs Fix" and is_complete: continue
                        if filter_status == "OK" and not is_complete: continue
                        
                        # Function Card
                        with st.expander(f"ƒ {fn['name']}", expanded=not is_complete):
                            
                            st.markdown(f"**Status:** {'🟢 Compliant' if is_complete else '🔴 Missing / Invalid Style'}")
                            
                            if not is_complete:
                                if st.button(f"✨ Generate {target_style.title()} Docstring", key=f"gen_{fn['name']}"):
                                    with st.spinner("Generating..."):
                                        st.session_state[f"preview_{fn['name']}"] = generate_docstring(fn, target_style)
                                
                                if f"preview_{fn['name']}" in st.session_state:
                                    new_doc = st.session_state[f"preview_{fn['name']}"]
                                    
                                    c_diff1, c_diff2 = st.columns(2)
                                    with c_diff1:
                                        st.caption("Current")
                                        st.code(fn.get("docstring", "# No docstring"), language="python")
                                    with c_diff2:
                                        st.caption("Proposed (AI)")
                                        st.code(new_doc, language="python")
                                    
                                    if st.button("✅ Accept & Apply", key=f"apply_{fn['name']}", type="primary"):
                                        apply_docstring(sel_file, fn, new_doc)
                                        st.toast(f"Updated {fn['name']}!", icon="🎉")
                                        
                                        del st.session_state[f"preview_{fn['name']}"]
                                        st.session_state["parsed_files"] = parse_path(scan_path)
                                        st.rerun()

# -------------------------------------------------
# 📊 Analytics View
# -------------------------------------------------
elif menu == "📊 Analytics":
    st.title("Code Metrics & Health")
    
    if "parsed_files" in st.session_state:
        files = st.session_state["parsed_files"]
        
        file_opts = [f["file_path"] for f in files]
        sel_metric_file = st.selectbox("Select File", file_opts)
        
        if sel_metric_file:
            with open(sel_metric_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            m_index = compute_maintainability(content)
            complexity = compute_complexity(content)
            
            m1, m2 = st.columns(2)
            m1.metric("Maintainability Index", f"{m_index:.2f}", help="Score 0-100. Higher is better.")
            m2.metric("Total Functions", len(complexity))
            
            st.subheader("Cyclomatic Complexity")
            
            if complexity:
                chart_data = {c["name"]: c["complexity"] for c in complexity}
                st.bar_chart(chart_data)
            else:
                st.info("No functions found to analyze.")
    else:
        st.warning("Please scan the project first.")