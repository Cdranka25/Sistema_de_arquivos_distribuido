import subprocess
import os

processes = []

services = [
    ("nodes/01_node", "01_server_node.py"),
    ("nodes/02_node", "02_server_node.py"),
    ("nodes/03_node", "03_server_node.py"),
    ("master", "master.py"),
    ("client", "client.py"),
]

print("\n")
for path, script in services:
    print(f"Iniciando {script}...")

    p = subprocess.Popen(
        ["python", script],
        cwd=path
    )

    processes.append(p)

print("\n Sistema iniciado!")

try:
    input("Pressione ENTER para encerrar tudo...\n")
finally:
    for p in processes:
        p.terminate()