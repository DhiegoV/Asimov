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

KP = 0.6
KI = 0
KD = 0.008
TP = 180 #130

# lado do sensor de lado, isso vai definir por onde o robo vai ultrapassar o
# obstaculo e as direcoes que ele vai tomar quando dentro da sala 3, na busca
# de vitimas, por exemplo
lado_sensor_lado = 'esquerda'

# pra se orientar na sala 3 em funcao do lado que o sensor estah, deve-se
# definir o lado que o sensor nao estah tambem
if lado_sensor_lado == 'esquerda':
	lado_contrario_sensor_lado = 'direita'
elif lado_sensor_lado == 'direita':
	lado_contrario_sensor_lado = 'esquerda'

def compensar_verde(momento):
	"""Compensa andando para realizar o trajeto do verde corretamente."""

	# momento eh em relacao ao verde
	if momento == 'antes':
		quanto_andar = 220
		vel_ajuste = 80
	else:
		quanto_andar = 50
		vel_ajuste = 60

	dir.run_to_rel_pos(position_sp=-quanto_andar, speed_sp=vel_ajuste)
	esq.run_to_rel_pos(position_sp=-quanto_andar, speed_sp=vel_ajuste)
	esq.wait_while('running')

def graus_robo_para_tacho_counts_motores(graus):
	"""Retorne quanto de tacho counts os motores giram o robo dados `graus`.
	
	Para girar(), eh util que quem chame diga quantos graus quer que o robo
	gire. No entanto, como nao temos um giroscopio, fazemos isso mandando um
	valor em tacho counts pra os dois motores, um girando em reverso, outro
	girando normalmente, isso faz com que o robo gire em seu proprio eixo.
	
	Esta funcao faz o trabalho de retornar o valor em tacho counts que eh
	preciso mandar pra os motores pra girar o robo dados `graus`.

	Note que, como nao temos um giroscopio, usamos um valor que sabemos que o
	robo gira 90 graus, por olhometro, e usamos ele como referencia pra regra
	de tres que realiza a conversao. Este valor eh definido abaixo, pra
	facilitar caso precise de ajuste.
	"""

	# valor de referencia de 90 graus, tc eh abreviacao de tacho counts
	giro_noventa_graus_em_tc = 400

	valor_tc = (giro_noventa_graus_em_tc * graus) / 90

	return valor_tc

def girar(sentido, graus=90, velocidade=300):
	"""Gire o robo no proprio eixo tantos `graus` no dado `sentido`.
	
	Parametros:
	`sentido` (string, 'esquerda' ou 'direita', case sensitive)
		eh o sentido que o robo gira;
	`graus` (float, por padrao 90)
		eh o tanto de graus que robo gira;
	`velocidade` (float, por padrao 300)
		eh a velocidade que o robo gira.
	"""

	# para uma explicacao disso, vide a definicao da funcao abaixo
	giro = graus_robo_para_tacho_counts_motores(graus)

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

def andar(distancia_rot, velocidade=100, sentido='frente', esperar_acabar=True):
	"""Faca o robo andar com os parametros informados.

	distancia_rot (float): distancia, dada em rotacoes;
	velocidade (inteiro): em rotacoes/segundo;
	sentido (string): 'frente' ou 'tras', case insensitive;
	"""

	# O robo, montado como estah, vai pra frente com distancia negativa e pra
	# tras com distancia positiva. O condicional abaixo faz com que ele sempre
	# ande no sentido desejado.
	if sentido.lower() == 'frente' and distancia_rot > 0:
		distancia_rot *= -1
	elif sentido.lower == 'tras' and distancia_rot < 0:
		distancia_rot *= -1

	# convertendo de rotacoes para o que o robo aceita, tacho counts
	tacho_counts = dir.count_per_rot * distancia_rot

	# bote pra andar
	dir.run_to_rel_pos(position_sp=tacho_counts, speed_sp=velocidade)
	esq.run_to_rel_pos(position_sp=tacho_counts, speed_sp=velocidade)

	# espere acabar de andar
	if esperar_acabar == True:
		esq.wait_while('running')

# pra testar
#andar(0.5, esperar_acabar=False)

def tem_obstaculo_no_lado():
	"""Retorne (booleano) se o sensor do lado (sensor_lado) ve obstaculo."""

	if sensor_lado.distance_centimeters < 30:
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
		pass

	# pare de andar
	dir.stop()
	esq.stop()

def ultrapassar_obstaculo():
	"""Ultrapasse o obstaculo usando o metodo do sensor de lado e em sua direcao."""

	# distancia em rotacao pra compensar o final do robo
	compensar_rot = 0.3

	# distancia em rotacao pra achar a linha no final
	ate_linha_rot = 0.5

	# 'antes' do obstaculo
	girar(lado_contrario_sensor_lado)
	andar_ate_ver_obstaculo()
	sleep(1)
	andar_ate_deixar_de_ver_obstaculo()
	andar(compensar_rot)
	# 'do lado' do obstaculo
	girar(lado_sensor_lado)
	andar_ate_ver_obstaculo()
	sleep(1)
	andar_ate_deixar_de_ver_obstaculo()
	andar(compensar_rot)
	girar(lado_sensor_lado)
	# vendo o 'depois do obstaculo'
	andar_ate_ver_obstaculo()
	andar(0.7)
	andar_ate_deixar_de_ver_obstaculo()
	andar(0.4, sentido='tras')
	girar(lado_contrario_sensor_lado)
	andar(0.5, sentido='tras')

#ultrapassar_obstaculo()

def parar():
	"""Para os motores da esteira imediatamente."""

	dir.stop()
	esq.stop()

def andar_pra_sempre(sentido='frente', velocidade=200):
	"""Ande pra sempre pra frente.

	Para parar, use parar().
	"""

	# O robo, montado como estah, vai pra frente com velocidade negativa e pra
	# tras com velocidade positiva. O condicional abaixo faz com que ele sempre
	# ande no sentido desejado.
	if sentido.lower() == 'frente' and velocidade > 0:
		velocidade *= -1
	elif sentido.lower == 'tras' and velocidade < 0:
		velocidade *= -1

	dir.run_forever(speed_sp=velocidade)
	esq.run_forever(speed_sp=velocidade)

# pra teste
#andar_pra_sempre(sentido='tras')

def tem_linha_se_aproximando(amostras):
	"""Retorne se ha pontos se aproximando continuamente.

	Pois isso eh um receptor de bolas no final do outro lado da sala 3.
	"""
	

def tem_linha_se_afastando(amostras):
	"""Retorne se ha pontos se afastando continuamente.

	Pois isso eh um receptor de bolas no comeco do outro lado da sala 3.
	"""

def tem_receptor_na_minha_frente():
	"""Retorne booleano se ha o receptor de vitimas na minha frente.

	Essa funcao deve ser executada quando um provavel receptor estiver na
	frente do robo, isto eh, quando o robo estiver de frente para algum dos
	cantos.

	A logica eh: Se tiver o receptor na minha frente, quando eu andar pro meio
	da pista, vou ver um vazio no lado. No entanto, se eu nao tiver vendo o
	receptor, quando olhar pro lado a partir do meio, vou ver a parede da sala
	imediatamente do meu lado.
	"""

	girar(lado_contrario_sensor_lado)

	# andar ate mais ou menos o meio
	andar(2)
	parar()
	sleep(0.2)

	# olhar pro lado
	lado = sensor_lado.distance_centimeters

	# se tiver mais que 20 cm no lado, eu tava na frente dum receptor
	if lado > 20:
		tava_na_minha_frente = True
	else:
		tava_na_minha_frente = False

	return tava_na_minha_frente

def andar_ate_bola():
	"""Anda em direcao a uma possivel bola, parando quando acha que ve."""

	print('to indo pra bola')

	andar_pra_sempre()

	while sensor_frente.distance_centimeters > 10:
		pass
	
	parar()
	sleep(2)

def abaixar_garra():
	"""Abaixe a garra."""

	# potencia por dois segundos
	motor_garra.run_timed(time_sp=3000, speed_sp=300)

	# espere acabar de baixar a garra
	motor_garra.wait_while('running')

	# da uma rezinha pra garantir que uma bola meia boca entra
	andar(0.5, sentido='tras')
	# compensar a rezinha
	andar(0.5)

def levantar_garra():
	"""Levante a garra e pare-a no ar, catapultando as bolas pra fora."""

	motor_garra.run_to_rel_pos(position_sp=-150, speed_sp=300, stop_action='hold')

# pra testar
#levantar_garra()

def pegar_bola():
	"""Articule a garra pra capturar uma bola na frente."""

	print('vou pegar bola')

	andar(0.5, sentido='tras')

	# dar meia volta
	girar('esquerda')
	girar('esquerda')

	andar(0.6, sentido='tras')

	abaixar_garra()

def procurar_bola():
	"""Realize o caminho de procura de bolas.

	Esta funcao deve ser chamada logo depois do robo perceber que viu o
	receptor de vitimas.
	"""

	print('\n -- PROCURANDO BOLA -- \n')

	# voltar pra frente do receptor
	andar(2, sentido='tras')

	# se colocar em posicao de procura
	girar(lado_contrario_sensor_lado)

	# pra ter uma orientacao
	amostra_atual = sensor_lado.distance_centimeters

	# comecar a procurar
	andar(3, esperar_acabar=False)

	while esq.is_running:

		print('escaneando')

		amostra_anterior = amostra_atual
		amostra_atual = sensor_lado.distance_centimeters

		if (amostra_anterior - amostra_atual) > 15:
			# opa, discrepancia grande

			print('\n -- VI BOLA! -- \n')
			Sound.beep()
			girar(lado_sensor_lado)
			andar_ate_bola()
			pegar_bola()
			andar_ate_proximo_canto()
			girar(lado_contrario_sensor_lado)
			andar_ate_proximo_canto()
			levantar_garra()

def andar_ate_proximo_canto():
	"""Anda ate o sensor_frente ver menos que 10."""

	andar_pra_sempre()

	while sensor_frente.distance_centimeters > 10:
		pass

def rotina_sala_3():
	"""Faca a sala 3.

	A partir do encontro com a parede oposta a rampa que garante que o robo ta
	dento da sala 3, essa funcao assume o controle.
	"""

	if tem_receptor_na_minha_frente():
		Sound.beep().wait()
		Sound.beep().wait()
		print('opa, receptor tava na minha frente')
		procurar_bola()

	else:
		print('opa, receptor NAO tava na minha frente')
		andar_ate_proximo_canto()

		if tem_receptor_na_minha_frente():
			Sound.beep().wait()
			Sound.beep().wait()
			print('opa, receptor tava na minha frente')
			procurar_bola()

		else:
			print('opa, receptor NAO tava na minha frente')
			andar_ate_proximo_canto()

			if tem_receptor_na_minha_frente():
				Sound.beep().wait()
				Sound.beep().wait()
				print('opa, receptor tava na minha frente')
				procurar_bola()

			else:
				print('opa, receptor NAO tava na minha frente')

	parar()
	sleep(5)

# pra teste
#rotina_sala_3()

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

def confirme_verde():
	"""Verifique se algum dos sensores ve verde e gire de acordo."""
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
	Verifique se o valor de reflectancia atual parece com o de reflectancia de verde.
	
	Retorna um booleano True se sim, False senao.
	"""

	if sensor_dir.value() in range(direita["verde_min"], direita["verde_max"]):
		return True
	elif sensor_esq.value() in range(esquerda["verde_min"], esquerda["verde_max"]):
		return True
	else:
		return False

def sat(giro):
	"""
	Satura o valor do giro para nao ultrapassar o valor maximo do motor.
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

def seguir_parede():
	"""Ande rente a parede da direita ate que encontre algo na frente, usando o sensor de lado."""

	andar_pra_sempre()

	while sensor_frente.distance_centimeters > 10:
		andar_pra_sempre()
		sleep(0.4)

		lado = sensor_lado.distance_centimeters
		distancia = 6
		if lado < distancia:
			girar('esquerda', 10)
		else:
			girar('direita', 10)

	parar()

# pra testar
#seguir_parede()

def relaxar_garra():
	"""Solte forca da garra."""

	motor_garra.stop(stop_action='coast')

def vejo_silver_tape():
	"""Retorne booleano se os sensores de reflectancia veem a silver tape.

	O intervalo que define se a reflectancia atual eh a de silver tape eh
	calibrado previamente e entao eh consultado aqui.
	"""

	if sensor_dir.value() in range(direita['silver_tape_min'], direita['silver_tape_max']) \
		  and sensor_esq.value() in range(esquerda['silver_tape_min'], esquerda['silver_tape_max']):

		# anda um pouco e verifica de novo
		andar(0.1)
		return sensor_dir.value() in range(direita['silver_tape_min'], direita['silver_tape_max']) \
			  and sensor_esq.value() in range(esquerda['silver_tape_min'], esquerda['silver_tape_max'])

	else:
		return False

def executar():
	pid = PID(KP, KI, KD)
	pid.SetPoint = 0
	botao = Button()

	achismos_rampa = 0
	to_na_rampa = False

	relaxar_garra()

	while not botao.any():
		if parece_verde():
			confirme_verde()

		if to_na_rampa == False and sensor_frente.distance_centimeters < 10:
			# ATENCAO! A condicao acima impede que depois de to_na_rampa ser
			# True, o robo faca obstaculo!  Ou seja, se der falha de progresso
			# na rampa e o ultimo marcador tiver antes de um obstaculo, o robo,
			# quando encontrar esse obstaculo, ele nao sera ultrapassado.  Ou
			# seja: O ULTIMO MARCADOR NAO PODE ESTAR ANTES DE ALGUM OBSTACULO

			Sound.beep()
			ultrapassar_obstaculo()

		if to_na_rampa == False and sensor_lado.distance_centimeters < 20:
			achismos_rampa += 1
			print('achismos_rampa:', achismos_rampa)

		certeza_rampa = 60
		if to_na_rampa == False and achismos_rampa > certeza_rampa:
			to_na_rampa = True
			Sound.beep().wait()
			Sound.beep().wait()
			parar()

		if to_na_rampa == True and sensor_lado.distance_centimeters > 30:
			# caso o sensor_lado esteja vendo muito, ele nao ve parede, logo,
			# entramos pelo lado oposto a ele, pois ele ve o meio da sala 3

			# anda pra nao girar e encontrar a parede na cara
			andar(0.5)

			# gira pra andar rente a parede
			girar(lado_sensor_lado)

			# anda pra nao ver a entrada da sala 3 com o sensor de lado e girar
			# de novo
			andar(1.8)

		if to_na_rampa == True and sensor_frente.distance_centimeters < 10:
			# to vendo uma possibilidade de receptor
			rotina_sala_3()

		if to_na_rampa == True and vejo_silver_tape():
			parar()
			Sound.beep().wait()
			sleep(0.1)
			Sound.beep().wait()
			sleep(0.1)
			Sound.beep().wait()
			# Sound.play('../gemidao_do_zap.wav')
			print('\n -- TO NA SALA 3 -- \n')
			sleep(10)

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

