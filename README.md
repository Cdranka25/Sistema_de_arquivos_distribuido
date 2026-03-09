# Sistema de Arquivos Distribuído

Este projeto implementa um Sistema de Arquivos Distribuído, inspirado em programas como DropBox ou Google Drive.

O sistema permite o armazenamento e recuperação de arquivos utilizando múltiplos nós de armazenamento distribuídos. A arquitetura do sistema foi projetada para garantir disponibilidade, escalabilidade e tolerância a falhas.

O sistema utiliza comunicação baseada em HTTP, permitindo que diferentes componentes do sistema se comuniquem através de requisições REST.

---

## Arquitetura do Sistema

    O sistema é composto por quatro tipos principais de componentes:

    Navegador
        |
    Client
        |
    Master
        |
    -----------------------
    |        |           |
    Node1   Node2       Node3

---

### Client

Responsável pela interface com o usuário, permitindo:

- Upload de arquivos
- Listagem de arquivos
- Download de arquivos

O cliente se comunica com o Master através de requisições HTTP.

---

### Master

O servidor Master atua como coordenador do sistema, sendo responsável por:

- Receber requisições do cliente
- Distribuir arquivos entre os nós de armazenamento
- Executar o algoritmo de balanceamento de carga
- Localizar arquivos durante operações de download

O Master utiliza o algoritmo Round-Robin para distribuição de arquivos entre os nós.

---

### Nodes

Os nós de armazenamento são responsáveis por:

- Armazenar arquivos recebidos
- Fornecer arquivos para download
- Responder requisições de listagem de arquivos
- Participar do algoritmo de eleição de líder

Cada node executa um servidor Flask independente.

---

## Algoritmos Utilizados

- Data Replication: garante que os arquivos existam em mais de um node.
- Round-Robin: Distribui os arquivos entre os nós de forma sequencial.
- Algoritmo Bully: Caso o server de um dos nós falhe, os demais nós detectam a falha e iniciam um processo de eleição. O nó com maior id assume automaticamente.

---

## Tecnologias Utilizadas

- Python
- Flask Framework
- Requests Library
- HTTP / REST API

---

## Como Executar o Sistema

*Executar no Terminal:* python run_system.py
Este comando irá iniciar:

- Client
- Master
- Nodes de armazenamento

Acesso através do navegador:
<http://localhost:4000>
