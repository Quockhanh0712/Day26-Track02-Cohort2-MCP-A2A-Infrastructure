import subprocess
import time
import os
import sys
import urllib.request
from pathlib import Path
from dotenv import load_dotenv
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Load env
load_dotenv(PROJECT_ROOT / ".env")
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
                    print(f"→ Killing process {pid} on port {port}...")
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
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False

def main():
    print("Stopping any processes on A2A ports...")
    for port in [8001, 8002, 8003]:
        kill_process_on_port(port)
        
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    print("Starting A2A Specialist Agents...")
    agents = {
        "search_agent": 8001,
        "database_agent": 8002,
        "synthesis_agent": 8003
    }
    
    processes = {}
    for name, port in agents.items():
        log_file = logs_dir / f"{name}.log"
        f_log = open(log_file, "w", encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", f"agents.{name}.agent:a2a_app", "--host", "127.0.0.1", "--port", str(port)],
            stdout=f_log,
            stderr=subprocess.STDOUT,
            cwd=str(PROJECT_ROOT),
            env=os.environ
        )
        processes[name] = (proc, f_log)
        
    print("Waiting for A2A agents to be ready...")
    for name, port in agents.items():
        url = f"http://127.0.0.1:{port}/.well-known/agent-card.json"
        if wait_for_agent(url, name):
            print(f"[OK] {name} is ready.")
        else:
            print(f"[FAIL] Timeout waiting for {name}.")
            
    print("Loading notebook...")
    notebook_path = PROJECT_ROOT / "day26_mcp_a2a_lab.ipynb"
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
        
    # Execute notebook
    print("Executing notebook...")
    ep = ExecutePreprocessor(timeout=600, kernel_name="day26-win-kernel")
    try:
        ep.preprocess(nb, {"metadata": {"path": str(PROJECT_ROOT)}})
        print("[OK] Notebook execution completed successfully.")
    except Exception as e:
        err_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"[FAIL] Error during notebook execution: {err_msg}")
        # Still write back the notebook so we see where it failed
    finally:
        with open(notebook_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)
        print("[OK] Notebook written back to disk.")
        
        # Stop servers
        print("Stopping A2A Specialist Agents...")
        for name, (proc, f_log) in processes.items():
            proc.terminate()
            f_log.close()
        print("Done.")

if __name__ == "__main__":
    main()
