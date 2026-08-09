"""
Unified startup script for the ASD Framework Web Application.
Starts both the FastAPI backend and React dev frontend.

Usage:
    python start_app.py
"""

import subprocess
import sys
import os
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()


def main():
    print("=" * 60)
    print("ASD Framework Web Application Launcher")
    print("=" * 60)

    # Ensure project root and src are on Python path
    env = os.environ.copy()
    python_path = str(PROJECT_ROOT / "src")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = python_path + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = python_path

    # Start FastAPI backend
    print("\n[1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "127.0.0.1", "--port", "8000", "--reload",
         "--reload-dir", str(PROJECT_ROOT / "backend")],
        cwd=str(PROJECT_ROOT),
        env=env,
    )

    # Start React frontend dev server
    frontend_dir = PROJECT_ROOT / "frontend"
    frontend_proc = None
    if (frontend_dir / "package.json").exists():
        print("[2/2] Starting React dev server on http://127.0.0.1:5173 ...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        frontend_proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_dir),
            env=env,
        )
    else:
        print("[2/2] Frontend not built. Run 'cd frontend && npm install && npm run dev' separately.")

    print("\n" + "=" * 60)
    print("Web Application Running:")
    print(f"  Frontend:  http://127.0.0.1:5173")
    print(f"  Backend:   http://127.0.0.1:8000")
    print(f"  API Docs:  http://127.0.0.1:8000/api/docs")
    print("=" * 60)
    print("Press Ctrl+C to stop all servers.\n")

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_proc.terminate()
        if frontend_proc:
            frontend_proc.terminate()
        print("All servers stopped.")


if __name__ == "__main__":
    main()
