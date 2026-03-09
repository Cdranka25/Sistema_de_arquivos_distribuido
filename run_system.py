# run_system.py
import subprocess
import os
import sys
import time

processes = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

services = [
    ("master", "master.py"),
    ("nodes/01_node", "01_server_node.py"),
    ("nodes/02_node", "02_server_node.py"),
    ("nodes/03_node", "03_server_node.py"),
    ("client", "client.py"),
]

print("\n")

for path, script in services:

    full_path = os.path.join(BASE_DIR, path)

    print(f"Iniciando {script}...")

    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR

    p = subprocess.Popen(
        [sys.executable, script],
        cwd=full_path,
        env=env
    )

    processes.append(p)

    time.sleep(0.6)

print("\nSistema iniciado!\n")

try:
    input("Pressione ENTER para encerrar tudo...\n")

finally:
    for p in processes:
        p.terminate()