from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

NODES = [
    "http://localhost:5001",
    "http://localhost:5002",
    "http://localhost:5003"
]

current_node = 0


@app.route("/status")
def status():
    return jsonify({"status": "master online"})


@app.route("/upload", methods=["POST"])
def upload():

    global current_node

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    # escolher node (round-robin)
    node = NODES[current_node]

    current_node = (current_node + 1) % len(NODES)

    files = {"file": (file.filename, file.stream)}

    response = requests.post(f"{node}/upload", files=files)

    return jsonify({
        "message": "Arquivo enviado",
        "node": node,
        "node_response": response.text
    })


if __name__ == "__main__":
    app.run(port=5000)