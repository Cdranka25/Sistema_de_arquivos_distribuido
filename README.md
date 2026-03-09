# Sistema de Arquivos Distribuído

Este projeto implementa um **Sistema de Arquivos Distribuído**, inspirado em serviços como **Dropbox** e **Google Drive**.

O sistema permite o **armazenamento, replicação e recuperação de arquivos** utilizando múltiplos nós de armazenamento distribuídos.

A arquitetura foi projetada para oferecer:

- Alta disponibilidade
- Tolerância a falhas
- Replicação automática de dados
- Escalabilidade

A comunicação entre os componentes do sistema é realizada através de **requisições HTTP utilizando uma API REST**.

---

# Arquitetura do Sistema

O sistema é composto por quatro tipos principais de componentes:

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

# Client

O **Client** é responsável pela interface com o usuário.

Ele fornece uma interface web que permite:

- Upload de arquivos
- Listagem de arquivos armazenados
- Download de arquivos
- Exclusão de arquivos
- Upload por arrastar e soltar (Drag and Drop)

O Client envia todas as requisições ao **Master**, que coordena as operações do sistema.

---

# Master

O servidor **Master** atua como coordenador central do sistema distribuído.

Ele é responsável por:

- Receber requisições do cliente
- Distribuir arquivos entre os nós de armazenamento
- Manter o metadata do sistema
- Garantir o fator de replicação dos arquivos
- Monitorar a disponibilidade dos nós
- Recuperar arquivos durante operações de download
- Propagar exclusões de arquivos entre os nós

O Master mantém um arquivo de metadata persistente: metadata.json
Esse arquivo armazena a relação entre **arquivos e os nós que possuem suas cópias**.

---

# Nodes

Os **Nodes** são responsáveis pelo armazenamento físico dos arquivos.

Cada node executa um servidor Flask independente e fornece endpoints HTTP para:

- Receber uploads de arquivos
- Fornecer arquivos para download
- Listar arquivos armazenados
- Excluir arquivos

Cada node mantém seu próprio diretório local de armazenamento.

---

# Replicação de Dados

Para garantir tolerância a falhas, o sistema utiliza **replicação de arquivos**.

O fator de replicação é definido pela constante: REPLICATION_FACTOR = 2
Isso significa que **cada arquivo será armazenado em pelo menos dois nós diferentes**.

Se uma réplica for perdida (por falha de um node), o Master executa automaticamente a recriação da réplica em outro node disponível.

---

# Monitoramento de Nós

O Master realiza verificações periódicas de disponibilidade dos nodes através do endpoint: /status

Nodes que não respondem são temporariamente removidos da lista de nodes ativos.
Isso evita que o sistema tente enviar arquivos para servidores indisponíveis.

---

# Monitoramento de Replicação

Uma rotina chamada **Replication Monitor** verifica continuamente se todos os arquivos mantêm o número mínimo de réplicas.

Caso um arquivo possua menos réplicas que o definido pelo sistema, o Master automaticamente:

1. Seleciona um node que possui o arquivo
2. Copia o arquivo para outro node disponível

Isso garante que o sistema mantenha sempre o nível correto de redundância.

---

# Reconstrução de Metadata

Caso o arquivo `metadata.json` seja perdido ou corrompido, o sistema pode reconstruir automaticamente o metadata.

Durante a inicialização do Master:

1. Cada node é consultado
2. Os arquivos armazenados em cada node são listados
3. O Master reconstrói a estrutura de metadata do sistema

---

# Exclusão Distribuída

Quando um usuário solicita a exclusão de um arquivo:

1. A requisição é enviada ao Master
2. O Master identifica todos os nodes que armazenam o arquivo
3. O Master envia requisições de exclusão para esses nodes
4. O arquivo é removido do metadata do sistema

---

# Execução Concorrente

Operações de rede entre Master e nodes são executadas de forma **concorrente**, permitindo:

- Upload mais rápido
- Replicação mais eficiente
- Exclusão paralela de arquivos

Isso reduz significativamente o tempo de resposta do sistema.

---

# Tecnologias Utilizadas

- **Python**
- **Flask Framework**
- **Requests Library**
- **HTTP / REST API**
- **JavaScript (Frontend)**
- **HTML / CSS**

---

# Como Executar o Sistema

Execute no terminal: python run_system.py
Esse comando iniciará automaticamente:

- Master
- Nodes de armazenamento
- Client Web

---

# Acesso ao Sistema

Abra o navegador em: http://localhost:4000/

A partir da interface web será possível:

- Enviar arquivos
- Listar arquivos armazenados
- Baixar arquivos
- Excluir arquivos