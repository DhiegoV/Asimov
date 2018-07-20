#!/usr/bin/env python3

from ev3dev.ev3 import LargeMotor, ColorSensor, UltrasonicSensor, MediumMotor, INPUT_1, INPUT_2, INPUT_3

# MOTORES
esq = LargeMotor('outA')
dir = LargeMotor('outB')
#motor_garra = LargeMotor('outC')
#motor_sensor = MediumMotor('outD')

# SENSORES
sensor_esq = ColorSensor(address=INPUT_1)
sensor_dir = ColorSensor(address=INPUT_2)
sensor_frente = UltrasonicSensor(address=INPUT_3)
sensor_lado = InfraredSensor('in4')

sensor_esq.mode = 'COL-REFLECT'
sensor_dir.mode = 'COL-REFLECT'

