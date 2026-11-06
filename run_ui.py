"""
One-click cross-platform launcher for the Streamlit Web Dashboard.
Auto-detects the virtual environment and launches http://localhost:8501.
"""
import sys
import subprocess
from pathlib import Path

def find_streamlit():
    candidates = [
        Path("venv/Scripts/streamlit.exe"),
        Path("../venv/Scripts/streamlit.exe"),
        Path("venv/bin/streamlit"),
        Path("../venv/bin/streamlit"),
    ]
    for p in candidates:
        if p.exists():
            return str(p.resolve())
    return None

def find_python():
    candidates = [
        Path("venv/Scripts/python.exe"),
        Path("../venv/Scripts/python.exe"),
        Path("venv/bin/python"),
        Path("../venv/bin/python"),
    ]
    for p in candidates:
        if p.exists():
            return str(p.resolve())
    return sys.executable

def main():
    st = find_streamlit()
    py = find_python()
    curr_dir = Path.cwd()
    
    app_path = "app.py" if (curr_dir / "app.py").exists() else "self_healing_pipeline/app.py"
    
    if st:
        cmd = [st, "run", app_path]
    else:
        cmd = [py, "-m", "streamlit", "run", app_path]
        
    print(f"🌐 Launching Streamlit Web Dashboard ({app_path})...\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Stopped server.")

if __name__ == "__main__":
    main()
