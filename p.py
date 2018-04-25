#!/usr/bin/env python3

from ev3dev.ev3 import *
from PID import PID


KP = 5.9
KI = 0
KD = 0
TP = 120
OFFSET = 0

#MOTORES
esq = LargeMotor('outA')
dir = LargeMotor('outB')
#motor_garra = LargeMotor('outC')
#motor_sensor = MediumMotor('outD')


#SENSORES
sensor_esq = ColorSensor(address=INPUT_1)
sensor_dir = ColorSensor(address=INPUT_2)
sonar = UltrasonicSensor(address=INPUT_3)

sensor_esq.mode = 'COL-REFLECT'
sensor_dir.mode = 'COL-REFLECT'

def sat(giro):
    POT_MAX = 1000
    POT_MIN = - 1000
    '''
    Satura o valor do giro para não ultrapassar o valor máximo do motor
    :para giro: KP*erro +ou- TP
    :return: O valor do giro saturado
    '''
    if giro > POT_MAX:
        return POT_MAX

    if giro < POT_MIN:
        return POT_MIN

    return giro

def executar():
    pid = PID(KP, KI, KD)
    pid.SetPoint = 0

    while True:
        erro = (sensor_dir.value() - sensor_esq.value())
        pid.update(erro)
        correcao = pid.output

        giro_dir = sat(TP - correcao)
        giro_esq = sat(TP + correcao)

        esq.run_forever(speed_sp=giro_esq*(-1))
        dir.run_forever(speed_sp=giro_dir*(-1))

executar()
