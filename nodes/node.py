from flask import Flask, request, send_from_directory, jsonify
import os
import requests
import threading
import time


class Node:

    def __init__(self, node_id, port, storage_path, nodes, master_url):

        self.NODE_ID = node_id
        self.PORT = port
        self.STORAGE = storage_path
        self.NODES = nodes
        self.MASTER_URL = master_url

        self.app = Flask(__name__)

        os.makedirs(self.STORAGE, exist_ok=True)

        self.setup_routes()

    def setup_routes(self):

        @self.app.route("/upload", methods=["POST"])
        def upload():

            if "file" not in request.files:
                return jsonify({"error": "Nenhum arquivo"}), 400

            file = request.files["file"]

            path = os.path.join(self.STORAGE, file.filename)

            file.save(path)

            return jsonify({"message": "Arquivo salvo"})


        @self.app.route("/files")
        def files():
            return jsonify(os.listdir(self.STORAGE))


        @self.app.route("/download/<filename>")
        def download(filename):

            path = os.path.join(self.STORAGE, filename)

            if not os.path.exists(path):
                return jsonify({"error": "Arquivo não encontrado"}), 404

            return send_from_directory(self.STORAGE, filename, as_attachment=True)


        @self.app.route("/delete/<filename>", methods=["DELETE"])
        def delete(filename):

            path = os.path.join(self.STORAGE, filename)

            if os.path.exists(path):
                os.remove(path)
                return jsonify({"message": "Arquivo removido"})

            return jsonify({"error": "Arquivo não encontrado"}), 404


        @self.app.route("/status")
        def status():
            return jsonify({"status": "online"})


    def check_master(self):

        while True:

            try:
                requests.get(
                    f"{self.MASTER_URL}/status",
                    timeout=3
                )

            except requests.RequestException:
                print("Master caiu")

            time.sleep(5)


    def run(self):

        threading.Thread(
            target=self.check_master,
            daemon=True
        ).start()

        self.app.run(port=self.PORT)