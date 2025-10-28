## Sistema de Logística (versão acadêmica)

Projeto simples de simulação de um fluxo logístico: recebimento de pedido, cálculo da melhor rota com base no galpão mais próximo do cliente e atualização do status. Foi feito de forma didática, como um trabalho de faculdade.

### Requisitos
- Python 3.10+ (sem dependências externas)
- Windows PowerShell ou terminal equivalente

### Estrutura principal
- `functions/recebe_pedido.py`: adiciona o pedido na fila e inicia os registros.
- `functions/processa_rotas.py`: escolhe o galpão mais próximo e define a rota.
- `functions/atualiza_status_pedido.py`: muda o status do pedido.
- `scripts/simular.py`: script utilitário para rodar o fluxo completo ou etapas.
- `scripts/lib/distancia.py`: cálculo de distância e seleção do melhor galpão.
- `data/` e `events/`: arquivos JSON que simulam banco, filas e eventos.

### Como rodar (passo a passo)
No PowerShell, entre na pasta do projeto e execute:

```bash
python scripts/simular.py reset   # limpa filas, notificações e logs
python scripts/simular.py         # roda o fluxo completo: recebe -> rotas -> status
```

Saída esperada (exemplo):

```json
{
  "r1": {"ok": true,  "pedidoId": "p-0100"},
  "r2": {"ok": true,  "pedidoId": "p-0100", "rota": "R-PREMIUM-GALPAO-CENTRO"},
  "r3": {"ok": true,  "pedidoId": "p-0100", "status": "EM_ROTA"}
}
```

Também é possível rodar cada etapa separadamente:

```bash
python scripts/simular.py reset
python scripts/simular.py recebe   # usa events/pedido.recebido.json
python scripts/simular.py rotas    # processa rotas para o pedido na fila
python scripts/simular.py status   # atualiza status usando events/pedido.status.json
```

### Como a “rota” é escolhida
1. O sistema lê o cliente do pedido e pega suas coordenadas (`latitude`, `longitude`) em `data/dynamodb/bancoClientes.json`.
2. Lê os galpões disponíveis em `data/dynamodb/bancoGalpoes.json`.
3. Calcula a distância euclidiana entre cliente e cada galpão:

   \(dist = \sqrt{(lat_1 - lat_2)^2 + (lon_1 - lon_2)^2}\)

4. Escolhe o galpão com menor distância.
5. Define o “tipo” da rota pelo valor do pedido:
   - maior que 150 → `R-PREMIUM`
   - caso contrário → `R-ECONOMICA`
6. Combina o tipo com o galpão: exemplo `R-PREMIUM-GALPAO-CENTRO`.

Toda a lógica de distância está em `scripts/lib/distancia.py` e a integração acontece em `functions/processa_rotas.py`.

### Dados gerados
- `data/filas/*.json`: simulação de filas (recebidos/processados).
- `data/notificacoes/filaNotificacoes.json`: notificações registradas.
- `data/logs/TabelaLogs.json`: logs simples do fluxo.
- `data/dynamodb/bancoLogistico.json`: “banco” com status, rota e galpão do pedido.

### Dicas rápidas
- Para testar outra rota sugerida, edite `events/pedido.processado.json`.
- Para mudar localizações, edite `data/dynamodb/bancoClientes.json` e `data/dynamodb/bancoGalpoes.json`.
- Se executar um arquivo da pasta `functions/` diretamente, ele já configura o caminho do projeto para funcionar no VS Code/PowerShell.

---
Trabalho acadêmico — objetivo didático, focado em clareza do fluxo e leitura de arquivos JSON.


