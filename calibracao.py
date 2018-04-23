#!/usr/bin/env python3
# 
# Consulta os valores dos sensores de cor quando no preto e no branco. Para
# que, dada a mesma entrada, os dois sensores emitam a mesma saida. Isto eh,
# calibrando-os.
#
# Este script entao salva estes valores num arquivo para que possam ser usados
# nos outros programas.

from ev3dev.ev3 import Button
from time import sleep
from os import system
from json import dump
from portas_modos import *

# escolhendo fonte legivel
system('setfont Lat15-TerminusBold14')

botao = Button()
def esperar_botao():
	# Para a execucao ate que um botao seja pressionado.

	# enquanto nenhum botao eh pressionado
	while not botao.any():
		sleep(0.1)

# PRETO
print("Coloque os dois sensores no preto")
esperar_botao()

direita["branco"] = sensor_dir.value()
esquerda["branco"] = sensor_esq.value()

print("pretos:")
print("esq:", esquerda["preto"], "dir:", direita["preto"])
esperar_botao()

# BRANCO
print("Coloque os dois sensores no branco")
esperar_botao()

direita["branco"] = sensor_dir.value()
esquerda["branco"] = sensor_esq.value()

print("brancos:")
print("esq:", esquerda["branco"], "dir:", direita["branco"])
esperar_botao()

# SALVANDO
arq_dir = open(w, "sensor_direita.json")
dump(direita, arq_dir)
arq_dir.close()

arq_esq = open(w, "sensor_esquerda.json")
dump(esquerda, arq_esq)
arq_esq.close()

print("Valores gravados com sucesso")
sleep(2)

