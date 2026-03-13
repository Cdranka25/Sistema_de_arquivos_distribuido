
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, request, Response, render_template, jsonify
import requests
from cluster_config import MASTER_URL

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nome de arquivo inválido"}), 400

    try:

        files = {"file": (file.filename, file.read())}

        response = requests.post(
            f"{MASTER_URL}/upload",
            files=files,
            timeout=15
        )

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get(
                "Content-Type", "application/json")
        )

    except requests.RequestException as e:

        print("Erro ao conectar ao master:", e)

        return jsonify({
            "error": "Master indisponível"
        }), 500


@app.route("/files")
def files():

    try:

        response = requests.get(
            f"{MASTER_URL}/files",
            timeout=10
        )

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get(
                "Content-Type", "application/json")
        )

    except requests.RequestException:

        return jsonify({
            "error": "Master indisponível"
        }), 500


@app.route("/download/<filename>")
def download(filename):

    try:

        r = requests.get(
            f"{MASTER_URL}/download/{filename}",
            stream=True,
            timeout=15
        )

        if r.status_code != 200:
            return jsonify({"error": "Arquivo não encontrado"}), 404

        return Response(
            r.iter_content(chunk_size=8192),
            content_type=r.headers.get(
                "Content-Type",
                "application/octet-stream"
            ),
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except requests.RequestException:

        return jsonify({
            "error": "Erro ao baixar arquivo"
        }), 500


@app.route("/delete/<filename>", methods=["DELETE"])
def delete(filename):

    try:

        response = requests.delete(
            f"{MASTER_URL}/delete/{filename}",
            timeout=10
        )

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get(
                "Content-Type",
                "application/json"
            )
        )

    except requests.RequestException:

        return jsonify({
            "error": "Master indisponível"
        }), 500


if __name__ == "__main__":
    app.run(port=4000)
