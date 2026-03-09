import requests

MASTER_URL = "http://localhost:5000"

def upload_file():

    path = input("Caminho do arquivo: ")

    with open(path, "rb") as f:
        files = {"file": f}

        r = requests.post(f"{MASTER_URL}/upload", files=files)

    print(r.text)


def list_files():

    r = requests.get(f"{MASTER_URL}/files")

    print("Arquivos no sistema:")
    print(r.text)


def download_file():

    name = input("Nome do arquivo: ")

    r = requests.get(f"{MASTER_URL}/download/{name}")

    with open(name, "wb") as f:
        f.write(r.content)

    print("Download concluído")


def menu():

    while True:

        print("\n1 - Upload")
        print("2 - Listar arquivos")
        print("3 - Download")
        print("4 - Sair")

        op = input("> ")

        if op == "1":
            upload_file()

        elif op == "2":
            list_files()

        elif op == "3":
            download_file()

        elif op == "4":
            break


menu()