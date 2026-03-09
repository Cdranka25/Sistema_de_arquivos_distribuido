import subprocess
import os

processes = []

services = [
    ("nodes/01_node", "server.py"),
    ("nodes/02_node", "server.py"),
    ("nodes/03_node", "server.py"),
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