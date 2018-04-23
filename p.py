#!/usr/bin/env python3

from ev3dev.ev3 import *
from portas_modos import *
from json import load

arq_dir = open(r, "sensor_direita.json")
direita = load(arq_dir)
arq_dir.close()

arq_esq = open(r, "sensor_esquerda.json")
esquerda = load(arq_esq)
arq_esq.close()

KP = 5.5
TP = 120
OFFSET = 0

def sat(giro):
	'''
	Satura o valor do giro para não ultrapassar o valor máximo do motor
	:para giro: KP*erro +ou- TP
	:return: O valor do giro saturado
	'''

	POT_MAX = 1000
	POT_MIN = -1000

	if giro > POT_MAX:
		return POT_MAX

	if giro < POT_MIN:
		return POT_MIN

	return giro

def get_valor_sensor_direita():
	# Retorna o valor do sensor da direita calibrado, na escala de 0-1000

	valor = (
		(direita["branco"] - sensor_dir.value()) /
		(direita["branco"] - direita["preto"])
	) * -1000 + 1000

	return valor

def get_valor_sensor_esquerda():
	# Retorna o valor do sensor da esquerda calibrado, na escala de 0-1000

	valor = (
		(esquerda["branco"] - sensor_esq.value()) /
		(esquerda["branco"] - esquerda["preto"])
	) * -1000 + 1000

	return valor

def executar():
	while True:
		erro = get_valor_sensor_direita() - get_valor_sensor_esquerda()
		p = KP * erro
		giro_dir = sat(TP + p)
		giro_esq = sat(TP - p)
		esq.run_forever(speed_sp=giro_esq)
		dir.run_forever(speed_sp=giro_dir)

executar()

