from scripts.lib.json_store import push_json_array, write_json, read_json
from datetime import datetime
import json


def handler(event, context=None):
	pedido = json.loads(event) if isinstance(event, str) else event
	enqueued_at = datetime.utcnow().isoformat()
	registro = { **pedido, "enqueuedAt": enqueued_at }
	push_json_array("data/filas/filaPedidosRecebidos.json", registro)
	push_json_array("data/notificacoes/filaNotificacoes.json", { "tipo": "NOVO_PEDIDO", "pedidoId": pedido["pedidoId"], "quando": enqueued_at })
	push_json_array("data/logs/TabelaLogs.json", { "origem": "recebePedido", "pedidoId": pedido["pedidoId"], "data": enqueued_at })

	banco = read_json("data/dynamodb/bancoLogistico.json", []) or []
	if not any(x.get("pedidoId") == pedido["pedidoId"] for x in banco):
		banco.append({ "pedidoId": pedido["pedidoId"], "status": "RECEBIDO", "rota": None })
		write_json("data/dynamodb/bancoLogistico.json", banco)
	return { "ok": True, "pedidoId": pedido["pedidoId"] }


if __name__ == "__main__":
	with open('events/pedido.recebido.json', 'r', encoding='utf-8') as f:
		print(handler(json.load(f)))
