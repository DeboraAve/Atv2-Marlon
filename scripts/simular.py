import json
import sys
import os
from pathlib import Path

# Garante que o projeto rode mesmo ao clicar "Run" no editor
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from scripts.lib.json_store import write_json
from functions.recebe_pedido import handler as recebe
from functions.processa_rotas import handler as rotas
from functions.atualiza_status_pedido import handler as status


def reset():
	write_json("data/filas/filaPedidosRecebidos.json", [])
	write_json("data/filas/filaPedidosProcessados.json", [])
	write_json("data/notificacoes/filaNotificacoes.json", [])
	write_json("data/logs/TabelaLogs.json", [])


def run_fluxo():
	with open('events/pedido.recebido.json', 'r', encoding='utf-8') as f:
		evt = json.load(f)
	r1 = recebe(evt)
	r2 = rotas({ "pedidoId": evt["pedidoId"] })
	r3 = status({ "pedidoId": evt["pedidoId"], "novoStatus": "EM_ROTA" })
	return { "r1": r1, "r2": r2, "r3": r3 }


if __name__ == "__main__":
	cmd = sys.argv[1] if len(sys.argv) > 1 else "fluxo"
	if cmd == "reset":
		reset()
		print("OK reset")
	elif cmd == "recebe":
		with open('events/pedido.recebido.json', 'r', encoding='utf-8') as f:
			print(recebe(json.load(f)))
	elif cmd == "rotas":
		with open('events/pedido.processado.json', 'r', encoding='utf-8') as f:
			print(rotas(json.load(f)))
	elif cmd == "status":
		with open('events/pedido.status.json', 'r', encoding='utf-8') as f:
			print(status(json.load(f)))
	else:
		print(run_fluxo())
