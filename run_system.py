import subprocess
import os

processes = []

services = [
    ("nodes/01_node", "01_server_node.py"),
    ("nodes/02_node", "02_server_node.py"),
    ("nodes/03_node", "03_server_node.py"),
    ("nodes/04_node", "04_server_node.py"),
    ("nodes/05_node", "05_server_node.py"),
    ("nodes/06_node", "06_server_node.py"),
    ("nodes/07_node", "07_server_node.py"),
    ("nodes/08_node", "08_server_node.py"),
    ("nodes/09_node", "09_server_node.py"),
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