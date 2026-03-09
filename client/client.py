from flask import Flask, request, redirect, Response
import requests

app = Flask(__name__)

MASTER_URL = "http://localhost:5000"


@app.route("/")
def home():
    return """
    <h1>Cliente - Sistema de Arquivos Distribuído</h1>

    <h2>Upload de Arquivo</h2>

    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Enviar">
    </form>

    <h2>Arquivos</h2>

    <a href="/files">Listar Arquivos</a>
    """


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    files = {"file": (file.filename, file.stream)}

    response = requests.post(f"{MASTER_URL}/upload", files=files)

    return response.text


@app.route("/files")
def files():

    response = requests.get(f"{MASTER_URL}/files")

    return str(response.json())


@app.route("/download/<filename>")
def download(filename):

    r = requests.get(f"{MASTER_URL}/download/{filename}", stream=True)

    return Response(
        r.iter_content(chunk_size=1024),
        content_type=r.headers["Content-Type"],
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

if __name__ == "__main__":
    app.run(port=4000)