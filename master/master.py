import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cluster_config import get_node_list, REPLICATION_FACTOR
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
import threading
import random
import requests
from flask import Flask, request, jsonify, Response
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


app = Flask(__name__)

NODES = get_node_list()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
LOG_FILE = os.path.join(DATA_DIR, "master.log")

metadata = {}

ALIVE_NODES = []
ALIVE_LOCK = threading.Lock()

EXECUTOR = ThreadPoolExecutor(max_workers=8)


def log(message):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.ctime()} - {message}\n")
    except Exception:
        pass


def load_metadata():
    global metadata
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r") as f:
                metadata = json.load(f)
            log("Metadata carregado do disco")
        except Exception:
            metadata = {}
            log("Erro ao carregar metadata")
    else:
        metadata = {}


def save_metadata():
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(metadata, f)
    except Exception:
        log("Erro ao salvar metadata")


@app.route("/status")
def status():
    return jsonify({"status": "master online"})


def check_node_once(node, timeout=2):
    try:
        r = requests.get(f"{node}/status", timeout=timeout)
        return node, r.status_code == 200
    except requests.RequestException:
        return node, False


def health_check_loop(poll_interval=5, timeout=2):
    global ALIVE_NODES
    while True:
        try:
            futures = []
            with ThreadPoolExecutor(max_workers=min(8, max(1, len(NODES)))) as ex:
                for n in NODES:
                    futures.append(ex.submit(check_node_once, n, timeout))

                alive_now = []
                for fut in as_completed(futures):
                    node, alive = fut.result()
                    if alive:
                        alive_now.append(node)

            with ALIVE_LOCK:
                ALIVE_NODES = alive_now

        except Exception as e:
            log(f"Health-check erro: {e}")

        time.sleep(poll_interval)


def get_alive_nodes_snapshot():
    with ALIVE_LOCK:
        return list(ALIVE_NODES)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nome de arquivo inválido"}), 400

    filename = file.filename
    file_bytes = file.read()

    available_nodes = get_alive_nodes_snapshot()

    if not available_nodes:
        log("UPLOAD falhou - nenhum node disponível")
        return jsonify({"error": "Nenhum node disponível"}), 500

    selected_nodes = random.sample(
        available_nodes,
        min(REPLICATION_FACTOR, len(available_nodes))
    )

    if filename not in metadata:
        metadata[filename] = []

    futures = {}
    for node in selected_nodes:
        futures[EXECUTOR.submit(_post_file_to_node, node,
                                filename, file_bytes)] = node

    succeeded = []
    for fut in as_completed(futures):
        node = futures[fut]
        try:
            ok = fut.result()
            if ok:
                if node not in metadata[filename]:
                    metadata[filename].append(node)
                succeeded.append(node)
            else:
                log(f"Falha ao enviar {filename} para {node}")
        except Exception as e:
            log(f"Exception ao enviar {filename} para {node}: {e}")

    if not metadata[filename]:
        log(f"UPLOAD falhou completamente para {filename}")
        return jsonify({"error": "Falha ao salvar arquivo"}), 500

    save_metadata()
    log(f"UPLOAD {filename} → {metadata[filename]}")

    return jsonify({
        "message": "Arquivo replicado",
        "nodes": metadata[filename]
    })


def _post_file_to_node(node, filename, file_bytes, timeout=6):
    try:
        files = {"file": (filename, file_bytes)}
        r = requests.post(f"{node}/upload", files=files, timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return False


@app.route("/files")
def list_files():
    return jsonify(list(metadata.keys()))


@app.route("/download/<filename>")
def download(filename):
    if filename not in metadata:
        return jsonify({"error": "Arquivo não encontrado"}), 404

    nodes = metadata[filename]
    alive_snapshot = set(get_alive_nodes_snapshot())
    ordered = sorted(nodes, key=lambda n: (0 if n in alive_snapshot else 1, n))

    for node in ordered:
        if node not in alive_snapshot:
            pass
        try:
            r = requests.get(f"{node}/download/{filename}",
                             stream=True, timeout=6)
            if r.status_code == 200:
                log(f"DOWNLOAD {filename} via {node}")
                return Response(
                    r.iter_content(chunk_size=8192),
                    content_type=r.headers.get(
                        "Content-Type", "application/octet-stream"),
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}"}
                )
        except requests.RequestException:
            continue

    log(f"DOWNLOAD falhou para {filename}")
    return jsonify({"error": "Arquivo indisponível"}), 404


@app.route("/delete/<filename>", methods=["DELETE"])
def delete(filename):
    if filename not in metadata:
        return jsonify({"error": "Arquivo não encontrado"}), 404

    nodes = metadata[filename]

    futures = [EXECUTOR.submit(
        _delete_file_on_node, node, filename) for node in nodes]
    for fut in as_completed(futures):
        try:
            fut.result()
        except Exception:
            pass

    del metadata[filename]
    save_metadata()
    log(f"DELETE {filename}")

    return jsonify({"message": "Arquivo removido"})


@app.route("/stop-node/<int:node_id>", methods=["POST"])
def stop_node(node_id):

    if node_id not in range(1, len(NODES) + 1):
        return jsonify({"error": "Node inválido"}), 400

    node_url = NODES[node_id - 1]

    ok = _stop_node(node_url)

    if ok:
        log(f"Node {node_id} desligado manualmente")
        return jsonify({"message": f"Node {node_id} parado"})
    else:
        return jsonify({"error": "Falha ao parar node"}), 500


def _delete_file_on_node(node, filename, timeout=5):
    try:
        requests.delete(f"{node}/delete/{filename}", timeout=timeout)
    except requests.RequestException:
        pass


def _stop_node(node, timeout=3):
    try:
        r = requests.post(f"{node}/simulate-failure", timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return False


def replication_monitor():
    while True:
        for filename, nodes in list(metadata.items()):
            alive_nodes = get_alive_nodes_snapshot()
            nodes[:] = [n for n in nodes if n in alive_nodes]

            if len(nodes) < REPLICATION_FACTOR:
                log(f"Replica insuficiente para {filename}")
                available_nodes = [
                    n for n in NODES if n not in nodes and n in alive_nodes]
                if not available_nodes or not nodes:
                    continue

                source_node = nodes[0]
                target_node = random.choice(available_nodes)

                try:
                    r = requests.get(
                        f"{source_node}/download/{filename}", timeout=6)
                    if r.status_code != 200:
                        log(f"Erro ao baixar {filename} de {source_node}")
                        continue
                    data = r.content
                    fut = EXECUTOR.submit(
                        _post_file_to_node, target_node, filename, data)
                    ok = fut.result(timeout=10)
                    if ok:
                        nodes.append(target_node)
                        save_metadata()
                        log(f"REPLICATION {filename} → {target_node}")
                except Exception as e:
                    log(f"Erro ao replicar {filename}: {e}")

            elif len(nodes) > REPLICATION_FACTOR:
                extra_nodes = nodes[REPLICATION_FACTOR:].copy()
                futures = [EXECUTOR.submit(
                    _delete_file_on_node, n, filename) for n in extra_nodes]
                for fut in as_completed(futures):
                    try:
                        fut.result()
                    except Exception:
                        pass
                for n in extra_nodes:
                    if n in nodes:
                        nodes.remove(n)
                        save_metadata()
                        log(f"Removida cópia extra de {filename} em {n}")

        time.sleep(10)


def rebuild_metadata():
    global metadata
    print("Reconstruindo metadata a partir dos nodes...")
    metadata = {}
    alive_snapshot = get_alive_nodes_snapshot()
    for node in NODES:
        try:
            r = requests.get(f"{node}/files", timeout=4)
            if r.status_code != 200:
                continue
            files = r.json()
            for filename in files:
                metadata.setdefault(filename, []).append(node)
        except Exception:
            continue
    save_metadata()
    print("Metadata reconstruído")


if __name__ == "__main__":
    print("Master iniciado")
    load_metadata()

    threading.Thread(target=health_check_loop, daemon=True).start()

    time.sleep(0.5)
    if not metadata:
        rebuild_metadata()

    threading.Thread(target=replication_monitor, daemon=True).start()

    app.run(port=5000)
