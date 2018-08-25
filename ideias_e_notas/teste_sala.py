#!usr/bin/env python3 
#-*- coding: UTF-8 -*-

from main import *
#mapear a sala 3 antes de comecar a testar o codigo do resgate de vitimas
#para o robo melhor se situar no ambiente!

#identificando rampa teno como metodo valores do sensor de lado
identificar valores do sensor_lado
se tem obstarculo no lado:
	verificar tempo em que sensor ver obstaculo
	se tempo for grande:
		subindo rampa
		seguir frente ate sensor_frente<10
		if sensor_frente<10:
			parar motor
			verificar se sensor lado esta na parede
			se sensor_na_parede:
				girar no sentido oposto ao sensor_lado
				verificar se sensor frente ver vitima
			se nao
				girar para sensor na parede
	senao:
		seguir linha normal
	
