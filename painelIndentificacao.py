import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT) # saida_verm_motorista
GPIO.setup(11, GPIO.OUT) # saida_verd_motorista
GPIO.setup(13, GPIO.OUT) # saida_verm_passageiro
GPIO.setup(15, GPIO.OUT) # saida_verd_passageiro


def setLedMotorista(statusEmbarque):
    if statusEmbarque == "Em Desembarque":
        GPIO.output(7, True)
        GPIO.output(11, False)
    elif statusEmbarque == "Finalizado":
        GPIO.output(7, False)
        GPIO.output(11, True)
    else:
        GPIO.output(7, False)
        GPIO.output(11, False)

def setLedPassageiro(statusEmbarque, statusPassagemSaida):
    if statusEmbarque == "Em Desembarque" and statusPassagemSaida == "atencao":
        GPIO.output(13, True)
        GPIO.output(15, False)
    elif statusEmbarque == "Em Desembarque"  and statusPassagemSaida == "segura":
        GPIO.output(13, False)
        GPIO.output(15, True)
    elif statusEmbarque == "Finalizado":
        GPIO.output(7, False)
        GPIO.output(11, False)


# setLedMotorista("Em Desembarque")

# setLedPassageiro("Em Desembarque", "atencao")