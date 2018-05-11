#!/usr/bin/env python3

from ev3dev.core import ColorSensor
from os import system
from time import sleep

def configurar():
	sensor = ColorSensor()
	sensor.mode = 'RGB-RAW'

def desenhar_grafico():
	system("clear")

	print("vermelho:", round(sensor.red/10)*"|")
	print("verde:   ", round(sensor.green/10)*"|")
	print("azul:    ", round(sensor.blue/10)*"|")

	sleep(0.01)


