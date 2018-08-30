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
from time import sleep
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

KP = 0.58
KI = 0
KD = 0.008
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


def girar(sentido, giro=360, velocidade=300):
	"""Gire o robo no proprio eixo o tanto informado em `giro` no dado sentido.

	Por padrao, gire 90 graus no dado sentido.
	"""

	if sentido == 'esquerda' and giro < 0:
		giro *= -1
	elif sentido == 'direita' and giro > 0:
		giro *= -1

	# com giro positivo, isso abaixo gira pra esquerda
	dir.run_to_rel_pos(position_sp=-giro, speed_sp=velocidade)
	esq.run_to_rel_pos(position_sp=giro, speed_sp=velocidade)

	# espera ate acabar
	esq.wait_while('running')

# pra teste
#girar('direita', 180)

def andar(distancia_rot, velocidade=100, sentido='frente'):
    """Faça o robo andar com os parametros informados.

    distancia_rot (float): distancia, dada em rotacoes;
    velocidade (inteiro): em rotacoes/segundo;
    sentido (string): 'frente' ou 'tras', case insensitive;
    """

    # O robo, montado como estah, vai pra frente com distancia negativa e pra
    # tras com distancia positiva. O condicional abaixo faz com que ele sempre
    # ande no sentido desejado.
    if sentido.lower() == 'frente' and distancia_rot > 0:
        distancia_rot *= -1
    elif sentido.lower() == 'tras' and distancia_rot < 0:
        distancia_rot *= -1

    # convertendo de rotacoes para o que o robo aceita, tacho counts
    tacho_counts = dir.count_per_rot * distancia_rot

    # bote pra andar
    dir.run_to_rel_pos(position_sp=tacho_counts, speed_sp=velocidade)
    esq.run_to_rel_pos(position_sp=tacho_counts, speed_sp=velocidade)

    # espere acabar de andar
    esq.wait_while('running')

def tem_obstaculo_no_lado():
    """Retorne (booleano) se o sensor do lado (sensor_lado) ve obstaculo."""

    if sensor_lado.distance_centimeters < 20:
        return True
    else:
        return False

def andar_ate_deixar_de_ver_obstaculo():
    """Nome autoexplicativo."""

    # ande eternamente
    dir.run_forever(speed_sp=-80)
    esq.run_forever(speed_sp=-80)

    # pare a execucao do codigo ate que obstaculo nao seja visto
    while tem_obstaculo_no_lado():
        pass

    print('nao vejo mais obstaculo')

    # pare de andar
    dir.stop()
    esq.stop()

def andar_ate_ver_obstaculo():
    """Nome autoexplicativo."""

    # ande eternamente
    dir.run_forever(speed_sp=-80)
    esq.run_forever(speed_sp=-80)

    # pare a execucao do codigo ate que obstaculo seja visto
    while not tem_obstaculo_no_lado():
        sleep(0.1)
        pass

    print('vi obstaculo do lado')

    # pare de andar
    dir.stop()
    esq.stop()

def ultrapassar_obstaculo():
    """Ultrapasse o obstaculo usando o metodo do sensor de lado e em sua direcao."""

    # distancia em rotacao pra compensar o final do robo
    compensar_rot = 0.3

    # distancia em rotacao pra achar a linha no final
    ate_linha_rot = 0.5

	# PELA DIREITA

    # 'antes' do obstaculo
    girar('direita')
    andar_ate_ver_obstaculo()
    sleep(1)
    andar_ate_deixar_de_ver_obstaculo()
    andar(compensar_rot)
    # 'do lado' do obstaculo
    girar('esquerda')
    andar_ate_ver_obstaculo()
    sleep(1)
    andar_ate_deixar_de_ver_obstaculo()
    andar(compensar_rot)
    girar('esquerda')
    # vendo o 'depois do obstaculo'
    andar_ate_ver_obstaculo()
    andar(0.7)
    andar_ate_deixar_de_ver_obstaculo()
    andar(0.4, sentido='tras')
    girar('direita')
    andar(0.5, sentido='tras')
	
    '''
	# PELA ESQUERDA

    # 'antes' do obstaculo
    girar('esquerda')
    andar_ate_ver_obstaculo()
    sleep(1)
    andar_ate_deixar_de_ver_obstaculo()
    andar(compensar_rot)
    # 'do lado' do obstaculo
    girar('direita')
    andar_ate_ver_obstaculo()
    sleep(1)
    andar_ate_deixar_de_ver_obstaculo()
    andar(compensar_rot)
    girar('direita')
    # vendo o 'depois do obstaculo'
    andar_ate_ver_obstaculo()
    andar(0.7)
    andar_ate_deixar_de_ver_obstaculo()
    andar(0.4, sentido='tras')
    girar('esquerda')
    andar(0.5, sentido='tras')
    '''

#ultrapassar_obstaculo()

def compensar_obstaculo():
	quanto_andar = 40
	velocidade = 100
	dir.run_to_rel_pos(position_sp=quanto_andar, speed_sp= velocidade)
	esq.run_to_rel_pos(position_sp=quanto_andar, speed_sp = velocidade)
	esq.wait_while('running')

def atras_eh_branco_branco():
	"""Retorne booleano se um pouco atras tem branco-branco.
	
	Porque ai se tiver branco-branco, temos um verde normal.
	"""

	quanto_andar_pra_tras = 0.18

	andar(quanto_andar_pra_tras, sentido='tras')

	# 6 eh a cor branca
	if sensor_esq.value() == 6 and sensor_dir.value() == 6:
		retorno = True
	else:
		retorno = False
	
	# compensar o que andou pra tras, pra nao ver o verde
	# de novo e ficar num loop
	andar(quanto_andar_pra_tras, sentido='frente')

	return retorno

def get_valor_sensor(lado):
	"""Retorne o valor do sensor do `lado` convertido para a escala de 0-1000.
	
	Parametro:
	`lado` eh 'direita' ou 'esquerda', case insensitive.
	"""

	if lado.lower() == 'direita':
		valor = (
			(direita["branco"] - sensor_dir.value()) /
			(direita["branco"] - direita["preto"])
		) * -1000 + 1000

	elif lado.lower() == 'esquerda':
		valor = (
			(esquerda["branco"] - sensor_esq.value()) /
			(esquerda["branco"] - esquerda["preto"])
		) * -1000 + 1000
	
	return valor

# pra teste
'''
while True:
	sleep(0.5)
	print('get_valor_sensor("direita"):', get_valor_sensor("direita"))

	#print('get_valor_sensor_direita:', get_valor_sensor_direita())
'''

def procurar_linha_girando(lado, sensor):
	"""Procura a linha no `lado` girando pro `lado` utilizando o sensor da `sensor` de reflectancia.
	
	Parametros:
	`lado` eh 'direita' ou 'esquerda', case insensitive;
	`sensor` eh 'direita' ou 'esquerda', case insensitive.
	"""

	# quanto girar pra corrigir um pouco
	giro = 10

	# o quanto, em reflectancia de 0-1000, eh preto
	preto_em_reflectancia = 400

	# enquanto o sensor da `sensor` nao ver linha em `lado`
	while get_valor_sensor(sensor) > preto_em_reflectancia:
		print('get_valor_sensor(', sensor, ')', get_valor_sensor(sensor))
		girar(lado, 10)
		sleep(0.1)

	print('opa, sensor da', sensor, 'viu a linha na', lado)

# pra testar
#procurar_linha_girando(lado='esquerda', sensor='direita')

def confirme_verde():
	"""Verifique se algum dos sensores vê verde e gire de acordo."""
	modo_anterior = sensor_esq.mode
	sensor_esq.mode = 'COL-COLOR'
	sensor_dir.mode = 'COL-COLOR'

	# o quanto andar para ignorar um verde pos-preto
	passar_direto_em_rot = 0.4

	# 3 eh a cor verde
	if sensor_esq.value() == 3 and sensor_dir.value() == 3:
		# verde-verde, meia volta

		girar('esquerda')
		girar('esquerda')
	
	elif sensor_esq.value() == 3:
		# verde na esquerda

		if atras_eh_branco_branco():
			# verde normal

			Sound.beep()
			compensar_verde("antes")
			girar('esquerda')
			compensar_verde("depois")
		else:
			# verde pos-preto
			Sound.beep().wait()
			Sound.beep().wait()
			andar(passar_direto_em_rot)

	elif sensor_dir.value() == 3:
		# verde na direita

		if atras_eh_branco_branco():
			# verde normal

			Sound.beep()
			compensar_verde("antes")
			girar('direita')
			compensar_verde("depois")
		else:
			# verde pos-preto
			Sound.beep().wait()
			Sound.beep().wait()
			andar(passar_direto_em_rot)

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

		if sensor_frente.distance_centimeters < 5:
			Sound.beep()
			print('\n -- VI OBSTACULO! -- \n')
			ultrapassar_obstaculo()

		erro = get_valor_sensor('direita') - get_valor_sensor('esquerda')
		pid.update(erro)
		correcao = pid.output

		giro_dir = sat(TP - correcao)
		giro_esq = sat(TP + correcao)

		esq.run_forever(speed_sp=giro_esq*(-1))
		dir.run_forever(speed_sp=giro_dir*(-1))

	esq.stop()
	dir.stop()


executar()

