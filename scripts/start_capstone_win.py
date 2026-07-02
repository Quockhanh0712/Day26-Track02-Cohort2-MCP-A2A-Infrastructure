import subprocess
import time
import os
import sys
import urllib.request
import json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path)

os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

def kill_process_on_port(port):
    try:
        output = subprocess.check_output(f'netstat -ano | findstr LISTENING | findstr :{port}', shell=True).decode()
        pids_killed = set()
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid not in pids_killed and pid != "0":
                    print(f"Killing process {pid} listening on port {port}...")
                    subprocess.call(f'taskkill /F /PID {pid}', shell=True)
                    pids_killed.add(pid)
    except subprocess.CalledProcessError:
        pass

def wait_for_agent(url, name, timeout=15):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    print(f"[OK] {name} is ready!")
                    return True
        except Exception:
            pass
        time.sleep(1)
    print(f"[FAIL] Timeout waiting for {name} @ {url}")
    return False

def main():
    print("==================================================")
    print("  Day 26 Capstone (Windows) — MCP + A2A Multi-Agent")
    print("==================================================")
    
    # 1. Kill old processes
    print("\n[1/3] Cleaning up old processes on ports 8000, 8001, 8002, 8003...")
    for port in [8000, 8001, 8002, 8003]:
        kill_process_on_port(port)
    
    time.sleep(1)
    
    # Ensure logs folder exists
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # 2. Start A2A Specialists
    print("\n[2/3] Starting A2A Specialist Agents...")
    agents = {
        "search_agent": 8001,
        "database_agent": 8002,
        "synthesis_agent": 8003
    }
    
    processes = {}
    for name, port in agents.items():
        log_file = logs_dir / f"{name}.log"
        print(f"Starting {name} on port {port}... (Logging to logs/{name}.log)")
        f_log = open(log_file, "w", encoding="utf-8")
        
        # Use sys.executable to run uvicorn in the current environment
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", f"agents.{name}.agent:a2a_app", "--host", "127.0.0.1", "--port", str(port)],
            stdout=f_log,
            stderr=subprocess.STDOUT,
            cwd=str(PROJECT_ROOT),
            env=os.environ
        )
        processes[name] = (proc, f_log)
        
    # Wait for all specialists to be ready
    print("\nWaiting for agents to be ready...")
    all_ready = True
    for name, port in agents.items():
        url = f"http://127.0.0.1:{port}/.well-known/agent-card.json"
        ready = wait_for_agent(url, name)
        all_ready = all_ready and ready
        
    if not all_ready:
        print("[FAIL] Some agents failed to start. Check logs/ for details.")
        # Terminate subprocesses
        for name, (proc, f_log) in processes.items():
            proc.terminate()
            f_log.close()
        sys.exit(1)
        
    print("\n[3/3] Launching ADK Web UI (orchestrator)...")
    print("URL: http://localhost:8000")
    print("Press Ctrl+C in terminal to stop everything.")
    
    try:
        # Launch ADK Web UI
        # Using subprocess.run so this script blocks and keeps specialists running
        subprocess.run(
            ["adk", "web", "agents/orchestrator"],
            cwd=str(PROJECT_ROOT),
            env=os.environ
        )
    except KeyboardInterrupt:
        print("\nStopping all processes...")
    finally:
        # Terminate all specialists
        for name, (proc, f_log) in processes.items():
            print(f"Stopping {name}...")
            proc.terminate()
            f_log.close()
        print("All processes stopped.")

if __name__ == "__main__":
    main()
