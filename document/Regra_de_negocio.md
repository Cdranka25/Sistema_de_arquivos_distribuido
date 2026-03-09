# Regra de Negócio

Projeto de sistema de arquivos distribuidos, inspirado no DropBox
    Nome do Projeto: Senhor dos Arquivos
    Integrantes: Caio Dalagnoli Dranka e Vinicius Muller

---

## RN01 — Replicação obrigatória de arquivos

*Descrição:*
    Todo arquivo enviado ao sistema deve ser armazenado em pelo menos dois nós de armazenamento distintos.

*Objetivo:*
    Garantir tolerância a falhas e alta disponibilidade dos dados dentro do sistema de arquivos distribuído.

*Funcionamento:*
    Quando um usuário envia um arquivo para o sistema através do cliente, o servidor Master recebe o arquivo e seleciona nós de armazenamento disponíveis. O arquivo é então replicado em dois nós diferentes.

*Justificativa:*
    A replicação de dados aumenta a confiabilidade e reduz o risco de perda de informações em sistemas distribuídos.

---

## RN02 — Distribuição de arquivos entre nós

*Descrição:*
    O servidor Master deve distribuir os arquivos enviados entre os nós de armazenamento disponíveis utilizando o algoritmo de Round-Robin.

*Objetivo:*
    Garantir uma distribuição equilibrada dos arquivos entre os nós, evitando sobrecarga em um único servidor.

*Funcionamento:*
    A cada novo upload de arquivo, o Master seleciona o próximo nó disponível na lista de nós utilizando um índice circular.

*Justificativa:*
    O algoritmo Round-Robin permite distribuir requisições de forma simples e eficiente em ambientes distribuídos.

---

## RN03 — Detecção de falha do servidor Master

*Descrição:*
    Os nós do sistema devem monitorar continuamente o estado do servidor Master para detectar possíveis falhas.

*Objetivo:*
    Permitir que o sistema detecte automaticamente a indisponibilidade do coordenador.

*Funcionamento:*
    Cada nó envia requisições periódicas ao endpoint /status do Master. Caso o Master não responda dentro do tempo esperado, o nó considera que ocorreu uma falha e inicia o processo de eleição de líder.

*Justificativa:*
    A detecção rápida de falhas é essencial para manter a disponibilidade do sistema distribuído.

---

## RN04 — Eleição automática de novo coordenador

*Descrição:*
    Quando o servidor Master falha, os nós devem executar o Algoritmo Bully para eleger um novo coordenador.

*Objetivo:*
    Garantir que o sistema continue operando mesmo após a falha do servidor principal.

*Funcionamento:*

1. Um nó detecta que o Master não está respondendo.
2. O nó inicia uma eleição enviando mensagens para nós com identificadores maiores.
3. Se nenhum nó com identificador maior responder, o nó atual assume o papel de novo Master.

*Justificativa:*
    O algoritmo Bully garante que o nó com maior prioridade ativo seja eleito como líder.

---

## RN05 — Recuperação de arquivos

*Descrição:*
    O sistema deve permitir a recuperação de arquivos armazenados em qualquer nó do sistema.

*Objetivo:*
    Garantir que os usuários possam acessar arquivos independentemente do nó onde foram armazenados.

*Funcionamento:*
    Quando um usuário solicita o download de um arquivo, o servidor Master verifica os nós disponíveis e solicita o arquivo ao nó que o possui.

*Justificativa:*
    Essa abordagem permite acesso transparente aos arquivos armazenados no sistema distribuído.

