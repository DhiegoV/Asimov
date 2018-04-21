#!/usr/bin/env python3

from ev3dev.ev3 import *
from portas_modos import *

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

def executar():
    while True:
        erro = (sensor_dir.value() - sensor_esq.value())
        p = KP * erro
        giro_dir = sat(TP + p)
        giro_esq = sat(TP - p)
        esq.run_forever(speed_sp=giro_esq)
        dir.run_forever(speed_sp=giro_dir)

executar()

