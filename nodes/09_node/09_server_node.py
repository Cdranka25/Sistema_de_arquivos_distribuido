from flask import Flask, request, send_from_directory
import os
import requests
import threading
import time

NODE_ID = 9
MASTER_URL = "http://localhost:5000"

NODES = {
    1: "http://localhost:5001",
    2: "http://localhost:5002",
    3: "http://localhost:5003",
    4: "http://localhost:5004",
    5: "http://localhost:5005",
    6: "http://localhost:5006",
    7: "http://localhost:5007",
    8: "http://localhost:5008",
    9: "http://localhost:5009"
}

app = Flask(__name__)

UPLOAD_FOLDER = "storage"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def check_master():

    while True:
        try:
            requests.get(f"{MASTER_URL}/status", timeout=2)
        except:
            print("Master não respondeu. Iniciando eleição...")
            threading.Thread(target=start_election).start()

        time.sleep(5)


def start_election():

    print(f"Node {NODE_ID} iniciou eleição")

    higher_nodes = [i for i in NODES if i > NODE_ID]

    responded = False

    for node_id in higher_nodes:

        try:
            r = requests.post(f"{NODES[node_id]}/election", timeout=2)

            if r.status_code == 200:
                responded = True
                print(f"Node {node_id} respondeu à eleição")

        except:
            print(f"Node {node_id} não respondeu")

    if not responded:
        become_master()


def become_master():
    print(f"Node {NODE_ID} virou o novo MASTER")


@app.route("/election", methods=["POST"])
def election():

    print(f"Node {NODE_ID} recebeu mensagem de eleição")
    threading.Thread(target=start_election).start()

    return "OK"


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    if file.filename == "":
        return "Nenhum arquivo"

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    return "Arquivo salvo no node"


@app.route("/files")
def files():
    return os.listdir(UPLOAD_FOLDER)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.route("/status")
def status():
    return "Node online"


if __name__ == "__main__":
    threading.Thread(target=check_master).start()
    app.run(port=5009)
