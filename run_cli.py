"""
One-click cross-platform launcher for the Conversational Terminal CLI.
Auto-detects the virtual environment whether executed from the root or subfolder.
"""
import sys
import subprocess
from pathlib import Path

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
    py = find_python()
    curr_dir = Path.cwd()
    
    # Check if interactive.py is in current directory or package
    if (curr_dir / "interactive.py").exists():
        cmd = [py, "interactive.py"]
    else:
        cmd = [py, "-m", "self_healing_pipeline.interactive"]
        
    print(f"🚀 Launching Self-Healing CLI with {py}...\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Exited.")

if __name__ == "__main__":
    main()
