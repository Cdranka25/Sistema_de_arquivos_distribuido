# Regra de Negócio

Projeto de sistema de arquivos distribuídos, inspirado no DropBox  
Nome do Projeto: Senhor dos Arquivos  
Integrantes: Caio Dalagnoli Dranka e Vinicius Muller

---

## RN01 — Replicação obrigatória de arquivos

*Descrição:*  
Todo arquivo enviado ao sistema deve ser armazenado em múltiplos nós de armazenamento distintos.

*Objetivo:*  
Garantir tolerância a falhas e alta disponibilidade dos dados dentro do sistema de arquivos distribuído.

*Funcionamento:*  
Quando um usuário envia um arquivo através do cliente, o servidor Master recebe o arquivo e seleciona nós de armazenamento disponíveis para armazenar as réplicas.

O número mínimo de réplicas é definido pelo fator de replicação configurado no sistema.

Exemplo no projeto:
REPLICATION_FACTOR = 2
Isso significa que cada arquivo será armazenado em pelo menos dois nós distintos.

*Justificativa:*  
A replicação de dados aumenta a confiabilidade do sistema e reduz o risco de perda de informações em caso de falha de um servidor.

---

## RN02 — Seleção de nós disponíveis para armazenamento

*Descrição:*  
O servidor Master deve selecionar apenas nós ativos para armazenar arquivos enviados pelos usuários.

*Objetivo:*  
Evitar que arquivos sejam enviados para nós indisponíveis.

*Funcionamento:*  
O Master mantém uma lista atualizada de nós disponíveis.  
Quando um arquivo é enviado, o Master seleciona aleatoriamente nós disponíveis dessa lista para armazenar as réplicas.

*Justificativa:*  
A seleção entre nós ativos evita falhas de comunicação e garante maior eficiência no armazenamento distribuído.

---

## RN03 — Monitoramento de disponibilidade dos nós

*Descrição:*  
O servidor Master deve monitorar continuamente o estado dos nós de armazenamento.

*Objetivo:*  
Garantir que apenas nós ativos sejam utilizados para operações de armazenamento e recuperação de arquivos.

*Funcionamento:*  
Uma rotina de monitoramento executa verificações periódicas no endpoint: /status de cada nó do sistema.
Caso um nó não responda dentro do tempo limite, ele é considerado indisponível e removido temporariamente da lista de nós ativos.

*Justificativa:*  
Esse mecanismo evita atrasos causados por tentativas de comunicação com nós offline.

---

## RN04 — Monitoramento de replicação

*Descrição:*  
O sistema deve garantir que todos os arquivos mantenham o número mínimo de réplicas definido.

*Objetivo:*  
Preservar a redundância dos dados caso algum nó falhe.

*Funcionamento:*  
Uma rotina periódica chamada *replication monitor* verifica o número de réplicas de cada arquivo armazenado.

Caso o número de réplicas seja menor que o fator de replicação:

1. Um nó que possui o arquivo é selecionado como fonte.
2. Um novo nó disponível é selecionado como destino.
3. O arquivo é copiado entre os nós.

Caso existam mais réplicas que o necessário, cópias extras podem ser removidas.

*Justificativa:*  
Esse mecanismo garante que os arquivos sempre mantenham o nível de redundância configurado no sistema.

---

## RN05 — Recuperação de arquivos

*Descrição:*  
O sistema deve permitir a recuperação de arquivos armazenados em qualquer nó disponível.

*Objetivo:*  
Garantir que os usuários possam acessar arquivos independentemente do nó onde foram armazenados.

*Funcionamento:*  
Quando um usuário solicita o download de um arquivo:

1. O cliente envia a requisição ao servidor Master.
2. O Master consulta o metadata do sistema para identificar os nós que possuem o arquivo.
3. O Master solicita o arquivo a um dos nós disponíveis.

Caso um nó não responda, o Master tenta automaticamente outro nó que possua uma cópia.

*Justificativa:*  
Essa abordagem permite acesso transparente aos arquivos armazenados no sistema distribuído.

---

## RN06 — Exclusão distribuída de arquivos

*Descrição:*  
A exclusão de arquivos deve ser propagada para todos os nós que armazenam o arquivo.

*Objetivo:*  
Garantir consistência entre os nós de armazenamento.

*Funcionamento:*  
Quando um usuário solicita a exclusão de um arquivo:

1. A requisição é enviada ao servidor Master.
2. O Master identifica todos os nós que armazenam o arquivo.
3. O Master envia requisições de exclusão para cada um desses nós.
4. Após a remoção, o arquivo é removido do metadata do sistema.

*Justificativa:*  
Esse processo evita inconsistências entre os nós e garante que o arquivo seja completamente removido do sistema.

---

## RN07 — Persistência de metadados

*Descrição:*  
O servidor Master deve manter um registro persistente dos arquivos armazenados e dos nós que contêm cada réplica.

*Objetivo:*  
Permitir que o sistema recupere seu estado após reinicializações.

*Funcionamento:*  
Os metadados do sistema são armazenados em um arquivo JSON chamado: metadata.json
Esse arquivo contém a relação entre os arquivos e os nós que armazenam suas cópias.

*Justificativa:*  
Sem persistência, o sistema perderia o controle da localização dos arquivos após reiniciar.

---

## RN08 — Reconstrução automática de metadata

*Descrição:*  
O sistema deve reconstruir automaticamente o metadata caso o arquivo de controle não esteja disponível.

*Objetivo:*  
Permitir recuperação do sistema após falhas ou perda do arquivo de metadata.

*Funcionamento:*  
Durante a inicialização do servidor Master:

1. O sistema verifica se o arquivo `metadata.json` existe.
2. Caso não exista, o Master consulta cada nó do sistema.
3. Cada nó retorna a lista de arquivos armazenados localmente.
4. O Master reconstrói o metadata com base nessas informações.

*Justificativa:*  
Esse mecanismo aumenta a resiliência do sistema.

---

## RN09 — Execução concorrente de operações de rede

*Descrição:*  
Operações de rede entre o Master e os nós devem ser executadas de forma concorrente sempre que possível.

*Objetivo:*  
Reduzir o tempo de resposta do sistema.

*Funcionamento:*  
O servidor Master executa operações de rede em paralelo para:

- envio de arquivos para múltiplos nós
- exclusão de arquivos em múltiplos nós
- verificação de disponibilidade dos nós

*Justificativa:*  
A execução concorrente evita atrasos causados por operações sequenciais em ambientes distribuídos.

---

## RN10 — Interface de acesso ao sistema

*Descrição:*  
O sistema deve fornecer uma interface web para interação com o usuário.

*Objetivo:*  
Permitir que usuários realizem operações básicas de gerenciamento de arquivos.

*Funcionalidades disponíveis:*

- upload de arquivos
- listagem de arquivos armazenados
- download de arquivos
- exclusão de arquivos
- seleção múltipla de arquivos
- suporte a arrastar e soltar arquivos (drag-and-drop)

*Justificativa:*  
Uma interface web facilita o uso do sistema e permite demonstrar o funcionamento do sistema distribuído de forma prática.
