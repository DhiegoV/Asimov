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

KP = 0.5
KI = 0
KD = 0
TP = 120

def compensar_verde(momento):
	# Anda um pouco para frente para evitar que o robo veja o verde novamente
	# apos o giro de 90

	# ate_eixo_rotacao eh a distancia em graus para o motor girar ate que o eixo de
	# rotacao do robo seja alcancado

	# TO DO!
	if momento == 'antes':
		ate_eixo_rotacao = 160
		v_ajuste = 80

	Sound.beep()
	dir.run_to_rel_pos(position_sp=-ate_eixo_rotacao, speed_sp=v_ajuste)
	esq.run_to_rel_pos(position_sp=-ate_eixo_rotacao, speed_sp=v_ajuste)
	esq.wait_while('running')


def girar(sentido):
	# Gira o robô no próprio eixo 90 graus no dado sentido

	velocidade = 400

	# direita é um vaor positivo e esquerda é um valr negativo, pois positivo
	# eh sentido horario
	# 90 graus p/ robo = 420 graus p/ motor
	quanto_rodar = 420

	if sentido == 'esquerda':
		compensar_verde()

		Sound.beep()
		dir.run_to_rel_pos(position_sp=-quanto_rodar, speed_sp=velocidade)
		esq.run_to_rel_pos(position_sp=quanto_rodar, speed_sp=velocidade)
		esq.wait_while('running')

		compensar_verde()
	elif sentido == 'direita':
		compensar_verde()

		Sound.beep()
		dir.run_to_rel_pos(position_sp=quanto_rodar, speed_sp=velocidade)
		esq.run_to_rel_pos(position_sp=-quanto_rodar, speed_sp=velocidade)
		esq.wait_while('running')

		compensar_verde()
	else:
		print('SENTIDO INFORMADO ERRONEAMENTE')

def rotina_verde():
	# Verifica se algum dos sensores vê verde e gira de acordo

	modo_anterior = sensor_esq.mode
	sensor_esq.mode = 'COL-COLOR'
	sensor_dir.mode = 'COL-COLOR'

	# se o sensor vê verde, cor 3
	if sensor_esq.value() == 3:
		girar('esquerda')
	elif sensor_dir.value() == 3:
		girar('direita')

	sensor_esq.mode = modo_anterior
	sensor_dir.mode = modo_anterior

def parece_verde():
	# Verifica se o valor de reflectancia atual parece com o de
	# reflectancia de verde, retornando True se sim, e False se não.

	if sensor_dir.value() in range(direita["verde_min"], direita["verde_max"]):
		return True
	elif sensor_esq.value() in range(esquerda["verde_min"], esquerda["verde_max"]):
		return True
	else:
		return False

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
	botao = Button()

	while not botao.any():
		if parece_verde():
			rotina_verde()

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

