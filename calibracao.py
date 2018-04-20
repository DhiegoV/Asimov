#!/usr/bin/env python3

from ev3dev.ev3 import Button
from time import sleep
from os import system
from portas_modos import *

# escolhendo fonte legivel
system('setfont Lat15-TerminusBold14')

botao = Button()
def esperar_botao():
	"""
	Para a execucao ate que um botao seja pressionado, emitindo um bipe quando eh.
	"""
	# enquanto nenhum botao eh pressionado
	while not botao.any():
		sleep(0.01)

