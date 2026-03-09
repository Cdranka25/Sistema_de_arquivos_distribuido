from flask import Flask, request, jsonify, Response
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


@app.route("/files")
def list_files():

    all_files = []

    for node in NODES:
        try:
            r = requests.get(f"{node}/files")

            if r.status_code == 200:
                all_files.extend(r.json())

        except:
            pass

    return jsonify(all_files)


@app.route("/download/<filename>")
def download(filename):

    for node in NODES:

        try:
            r = requests.get(f"{node}/download/{filename}", stream=True)

            if r.status_code == 200:
                return Response(
                    r.iter_content(chunk_size=1024),
                    content_type=r.headers["Content-Type"],
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}"
                    }
                )

        except:
            continue

    return {"error": "Arquivo não encontrado"}, 404


if __name__ == "__main__":
    app.run(port=5000)
