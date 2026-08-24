# -*- coding: utf-8 -*-
"""
Unified launcher for the PharmaPolySCOPE Web Application.
Compatible with Python 2.7+ and Python 3.x.
"""

import sys
import os
import subprocess
import time

# Auto-redirect Python 2 to Python 3 launcher
if sys.version_info[0] < 3:
    print("=" * 60)
    print("NOTICE: 'python' is configured to Python 2.7 on this machine.")
    print("Launching with Python 3 launcher ('py -3')...")
    print("=" * 60)
    script_path = os.path.abspath(__file__)
    res = subprocess.call(["py", "-3", script_path] + sys.argv[1:])
    sys.exit(res)

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()


def main():
    print("=" * 60)
    print("PharmaPolySCOPE Web Application Launcher")
    print("Developed by Tushar Mathapati")
    print("=" * 60)

    # Ensure project root and src are on Python path
    env = os.environ.copy()
    python_path = str(PROJECT_ROOT / "src")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = python_path + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = python_path

    # Use Python 3 executable
    py3_exe = sys.executable

    # Start FastAPI backend
    print("\n[1/2] Starting FastAPI server on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [py3_exe, "-m", "uvicorn", "backend.main:app",
         "--host", "127.0.0.1", "--port", "8000", "--reload",
         "--reload-dir", str(PROJECT_ROOT / "backend")],
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    # Start React frontend dev server if available
    frontend_dir = PROJECT_ROOT / "frontend"
    frontend_proc = None
    if (frontend_dir / "package.json").exists():
        print("[2/2] Starting React dev server on http://127.0.0.1:5173 ...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        try:
            frontend_proc = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=str(frontend_dir),
                env=env,
            )
        except Exception as e:
            print("Warning: Could not start npm dev server: {}".format(e))

    print("\n" + "=" * 60)
    print("ASD Web Application Running:")
    print("  Frontend UI : http://localhost:5173 (or http://127.0.0.1:8000)")
    print("  FastAPI Docs: http://127.0.0.1:8000/api/docs")
    print("=" * 60)
    print("Press Ctrl+C to stop all servers.\n")

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        print("Servers stopped cleanly.")


if __name__ == "__main__":
    main()
