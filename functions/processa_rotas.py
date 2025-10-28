import sys
from pathlib import Path

# Garante que o projeto rode mesmo ao clicar "Run" no editor
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))
import os
os.chdir(PROJECT_ROOT)

from scripts.lib.json_store import read_json, write_json, push_json_array
from scripts.lib.distancia import encontra_melhor_galpao
from datetime import datetime
import json


def handler(event=None, context=None):
	fila = read_json("data/filas/filaPedidosRecebidos.json", []) or []
	pedido = None
	if event and isinstance(event, dict) and event.get("pedidoId"):
		# Se event tem pedidoId, busca o pedido completo na fila
		pedido_id_event = event.get("pedidoId")
		for p in fila:
			if p.get("pedidoId") == pedido_id_event:
				pedido = p
				fila.remove(p)
				break
		# Se não encontrou na fila, usa o event como pedido básico
		if not pedido:
			pedido = event
	elif fila:
		pedido = fila.pop(0)
	else:
		return { "ok": False, "motivo": "Sem pedidos na fila" }

	# Busca dados do cliente para obter coordenadas
	clientes = read_json("data/dynamodb/bancoClientes.json", []) or []
	cliente = next((c for c in clientes if c.get("clienteId") == pedido.get("clienteId")), None)
	
	# Busca galpões disponíveis
	galpoes = read_json("data/dynamodb/bancoGalpoes.json", []) or []
	
	# Determina o galpão mais próximo baseado na distância
	melhor_galpao = None
	rota = (event or {}).get("rotaSugerida")
	
	if cliente and galpoes and pedido.get("clienteId"):
		cliente_lat = cliente.get("latitude")
		cliente_lon = cliente.get("longitude")
		
		if cliente_lat is not None and cliente_lon is not None:
			melhor_galpao = encontra_melhor_galpao(cliente_lat, cliente_lon, galpoes)
			if melhor_galpao:
				# Se valor > 150, usa rota premium, senão usa econômica
				valor_total = pedido.get("valorTotal", 0)
				tipo_rota = "R-PREMIUM" if (valor_total > 150) else "R-ECONOMICA"
				rota = f"{tipo_rota}-{melhor_galpao.get('galpaoId')}"
	
	# Fallback para rota padrão se não encontrar galpão ou não tiver coordenadas
	if not rota:
		rota = ("R-PREMIUM" if (pedido.get("valorTotal", 0) > 150) else "R-ECONOMICA")

	banco = read_json("data/dynamodb/bancoLogistico.json", []) or []
	existente = next((x for x in banco if x.get("pedidoId") == pedido["pedidoId"]), { "pedidoId": pedido["pedidoId"] })
	existente["status"] = "PROCESSADO"
	existente["rota"] = rota
	if melhor_galpao:
		existente["galpaoId"] = melhor_galpao.get("galpaoId")
		existente["galpaoNome"] = melhor_galpao.get("nome")
	write_json("data/dynamodb/bancoLogistico.json", [x for x in banco if x.get("pedidoId") != pedido["pedidoId"]] + [existente])

	write_json("data/filas/filaPedidosRecebidos.json", fila)
	push_json_array("data/filas/filaPedidosProcessados.json", { "pedidoId": pedido["pedidoId"], "rota": rota })
	push_json_array("data/notificacoes/filaNotificacoes.json", { "tipo": "PEDIDO_PROCESSADO", "pedidoId": pedido["pedidoId"], "rota": rota, "quando": datetime.utcnow().isoformat() })
	push_json_array("data/logs/TabelaLogs.json", { "origem": "processaRotas", "pedidoId": pedido["pedidoId"], "rota": rota, "data": datetime.utcnow().isoformat() })

	return { "ok": True, "pedidoId": pedido["pedidoId"], "rota": rota }


if __name__ == "__main__":
	with open('events/pedido.processado.json', 'r', encoding='utf-8') as f:
		print(handler(json.load(f)))
