#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

print("# carregando bibliotecas")
print("ev3dev.ev3")
from ev3dev.ev3 import *
print("configuracao de portas e modos")
from portas_modos import *
print("json")
from json import load
print("PID")
from PID import PID
print("# carregamento completo")

print("# lendo arquivos de calibracao")
print("direita")
arq_dir = open("sensor_direita.json")
direita = load(arq_dir)
arq_dir.close()

print("esquerda")
arq_esq = open("sensor_esquerda.json")
esquerda = load(arq_esq)
arq_esq.close()
print("# leitura finalizada")

KP = 0.5
KI = 0
KD = 0
TP = 180 #130

def compensar_verde(momento):
	"""Compensa andando para realizar o trajeto do verde corretamente."""

	# momento é em relação ao verde
	if momento == 'antes':
		quanto_andar = 160
		vel_ajuste = 80
	else:
		quanto_andar = 50
		vel_ajuste = 60

	dir.run_to_rel_pos(position_sp=-quanto_andar, speed_sp=vel_ajuste)
	esq.run_to_rel_pos(position_sp=-quanto_andar, speed_sp=vel_ajuste)
	esq.wait_while('running')


def girar(sentido):
	"""Gire o robô no próprio eixo 90 graus no dado sentido."""

	velocidade = 400

	# Direita é um valor positivo e esquerda é um valor negativo.
	# Positivo = sentido horário.
	# 90 graus p/ robo = 420 graus p/ motor.
	quanto_rodar = 400 #420

	if sentido == 'esquerda':
		dir.run_to_rel_pos(position_sp=-quanto_rodar, speed_sp=velocidade)
		esq.run_to_rel_pos(position_sp=quanto_rodar, speed_sp=velocidade)
		esq.wait_while('running')

	elif sentido == 'direita':
		dir.run_to_rel_pos(position_sp=quanto_rodar, speed_sp=velocidade)
		esq.run_to_rel_pos(position_sp=-quanto_rodar, speed_sp=velocidade)
		esq.wait_while('running')

	else:
		print('SENTIDO INFORMADO ERRONEAMENTE')

def confirme_verde():
	"""Verifique se algum dos sensores vê verde e gire de acordo."""
	modo_anterior = sensor_esq.mode
	sensor_esq.mode = 'COL-COLOR'
	sensor_dir.mode = 'COL-COLOR'

	# se o sensor vê verde, cor 3
	if sensor_esq.value() == 3:
		Sound.beep()
		compensar_verde("antes")
		girar('esquerda')
		compensar_verde("depois")

	elif sensor_dir.value() == 3:
		Sound.beep()
		compensar_verde("antes")
		girar('direita')
		compensar_verde("depois")

	sensor_esq.mode = modo_anterior
	sensor_dir.mode = modo_anterior

def parece_verde():
	"""
	Verifique se o valor de reflectância atual parece com o de reflectância de verde.
	
	Retorna um booleano True se sim, False senão.
	"""

	if sensor_dir.value() in range(direita["verde_min"], direita["verde_max"]):
		return True
	elif sensor_esq.value() in range(esquerda["verde_min"], esquerda["verde_max"]):
		return True
	else:
		return False

def sat(giro):
	"""
	Satura o valor do giro para não ultrapassar o valor máximo do motor.
	:para giro: KP*erro +ou- TP
	:return: O valor do giro saturado
	"""

	POT_MAX = 1000
	POT_MIN = -1000

	if giro > POT_MAX:
		return POT_MAX

	if giro < POT_MIN:
		return POT_MIN

	return giro

def get_valor_sensor_direita():
	"""Retorne o valor do sensor direito convertido para a escala de 0-1000."""

	valor = (
		(direita["branco"] - sensor_dir.value()) /
		(direita["branco"] - direita["preto"])
	) * -1000 + 1000

	return valor

def get_valor_sensor_esquerda():
	"""Retorne o valor do sensor esquerdo convertido para a escala de 0-1000."""

	valor = (
		(esquerda["branco"] - sensor_esq.value()) /
		(esquerda["branco"] - esquerda["preto"])
	) * -1000 + 1000

	return valor

def executar():
	pid = PID(KP, KI, KD)
	pid.SetPoint = 0
	botao = Button()

	while not botao.any():
		if parece_verde():
			confirme_verde()

		erro = get_valor_sensor_direita() - get_valor_sensor_esquerda()
		pid.update(erro)
		correcao = pid.output

		giro_dir = sat(TP - correcao)
		giro_esq = sat(TP + correcao)

		esq.run_forever(speed_sp=giro_esq*(-1))
		dir.run_forever(speed_sp=giro_dir*(-1))

	esq.stop()
	dir.stop()


executar()

