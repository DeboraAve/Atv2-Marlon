from math import sqrt


def calcula_distancia_euclidiana(ponto1, ponto2):
	"""
	Calcula a distância euclidiana entre dois pontos geográficos.
	
	Args:
		ponto1: tupla (latitude, longitude) do primeiro ponto
		ponto2: tupla (latitude, longitude) do segundo ponto
		
	Returns:
		float: distância euclidiana entre os dois pontos
	"""
	if not ponto1 or not ponto2:
		return float('inf')
	
	if len(ponto1) < 2 or len(ponto2) < 2:
		return float('inf')
	
	lat1, lon1 = ponto1
	lat2, lon2 = ponto2
	
	# Cálculo da distância euclidiana
	distancia_ao_quadrado = (lat1 - lat2)**2 + (lon1 - lon2)**2
	
	# Retorna a raiz quadrada (distância)
	return sqrt(distancia_ao_quadrado)


def encontra_melhor_galpao(cliente_lat, cliente_lon, galpoes):
	"""
	Encontra o galpão mais próximo do cliente baseado na distância euclidiana.
	
	Args:
		cliente_lat: latitude do cliente
		cliente_lon: longitude do cliente
		galpoes: lista de dicionários com dados dos galpões
		
	Returns:
		dict: galpão mais próximo ou None se não encontrar
	"""
	if not galpoes:
		return None
	
	melhor_galpao = None
	menor_distancia = float('inf')
	
	ponto_cliente = (cliente_lat, cliente_lon)
	
	for galpao in galpoes:
		lat = galpao.get('latitude')
		lon = galpao.get('longitude')
		
		if lat is None or lon is None:
			continue
		
		ponto_galpao = (lat, lon)
		distancia = calcula_distancia_euclidiana(ponto_cliente, ponto_galpao)
		
		if distancia < menor_distancia:
			menor_distancia = distancia
			melhor_galpao = galpao
	
	return melhor_galpao


if __name__ == "__main__":
	# Teste da função
	cliente = (2, 3)
	galpao_1 = (2, 4)
	galpao_2 = (3, 4)
	
	print(f"Distancia cliente para galpao 1: {calcula_distancia_euclidiana(cliente, galpao_1)}")
	print(f"Distancia cliente para galpao 2: {calcula_distancia_euclidiana(cliente, galpao_2)}")
