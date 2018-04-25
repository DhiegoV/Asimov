#!/usr/bin/env python3

from ev3dev.ev3 import *
from portas_modos import *
from json import load
from PID import PID

arq_dir = open("sensor_direita.json")
direita = load(arq_dir)
arq_dir.close()

arq_esq = open("sensor_esquerda.json")
esquerda = load(arq_esq)
arq_esq.close()

KP = 0.7
KI = 0
KD = 0
TP = 120

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
	pid = PID(KP, KI, KD)
	pid.SetPoint = 0

	while True:
		erro = get_valor_sensor_direita() - get_valor_sensor_esquerda()
		pid.update(erro)
		correcao = pid.output

		giro_dir = sat(TP - correcao)
		giro_esq = sat(TP + correcao)

		esq.run_forever(speed_sp=giro_esq*(-1))
		dir.run_forever(speed_sp=giro_dir*(-1))

executar()

