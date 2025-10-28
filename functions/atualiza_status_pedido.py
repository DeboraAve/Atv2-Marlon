from scripts.lib.json_store import read_json, write_json, push_json_array
from datetime import datetime
import json


def handler(event=None, context=None):
	pedido_id = None
	novo_status = None
	if event and isinstance(event, dict) and event.get("pedidoId"):
		pedido_id = event["pedidoId"]
		novo_status = event.get("novoStatus", "ENTREGUE")
	else:
		fila = read_json("data/filas/filaPedidosProcessados.json", []) or []
		if not fila:
			return { "ok": False, "motivo": "Sem pedidos processados" }
		msg = fila.pop(0)
		pedido_id = msg["pedidoId"]
		novo_status = "EM_ROTA"
		write_json("data/filas/filaPedidosProcessados.json", fila)

	banco = read_json("data/dynamodb/bancoLogistico.json", []) or []
	existente = next((x for x in banco if x.get("pedidoId") == pedido_id), None)
	if not existente:
		return { "ok": False, "motivo": "Pedido inexistente" }

	existente["status"] = novo_status
	write_json("data/dynamodb/bancoLogistico.json", [x for x in banco if x.get("pedidoId") != pedido_id] + [existente])

	push_json_array("data/logs/TabelaLogs.json", { "origem": "atualizaStatusPedido", "pedidoId": pedido_id, "status": novo_status, "data": datetime.utcnow().isoformat() })
	push_json_array("data/notificacoes/filaNotificacoes.json", { "tipo": "STATUS_ATUALIZADO", "pedidoId": pedido_id, "status": novo_status, "quando": datetime.utcnow().isoformat() })

	return { "ok": True, "pedidoId": pedido_id, "status": novo_status }


if __name__ == "__main__":
	with open('events/pedido.status.json', 'r', encoding='utf-8') as f:
		print(handler(json.load(f)))
