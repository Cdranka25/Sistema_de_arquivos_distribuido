from flask import Flask, request, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = "storage"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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
    app.run(port=5002)