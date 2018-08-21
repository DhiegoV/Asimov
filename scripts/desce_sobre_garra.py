#!/bin/env python3

from portas_modos import motor_garra

def descer_garra():
    # a partir da posicao 'guardada', desca a garra

    delta_em_rot = -0.5

    motor_garra.run_to_abs_pos(position_sp=delta_em_rot)

def subir_garra():
    # a partir da posicao 'abaixada', suba a garra

    delta_em_rot = 0.5

    motor_garra.run_to_abs_pos(position_sp=delta_em_rot)

descer_garra()
subir_garra()

