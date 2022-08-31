"""
Faculdade de Tecnologia de Jundiaí
Programação para Sistemas Embarcados I
CCS811: Sensor de qualidade do ar
        Concentração de eCO2 em ppm e de tVOC em ppb
Data: maio 2022

Com base nos dados contidos na folha de especificações do CCS811
     e nas bibliotecas Adafruit e Sparkfun
     
MicroPython v1.18 17-01-2022; Módulo ESP com ESP32
"""

from machine import I2C

class CCS811(object):
    def __init__(self, i2c=None, addr=90):
        self.i2c = i2c
        self.addr = addr    # 0x5A = 90, 0x5B = 91
        self.tVOC = 0
        self.eCO2 = 0
        self.mode = 1       # Modo de energia constante: medidas a cada segundo
        self.error = False
        # Verifica se o sensor está disponível no endereço de rede I2C
        devices = i2c.scan()
        if self.addr not in devices:
            raise ValueError('CCS811 não encontrado. Por favor verifique a interface. Coloque Wake para terra.')
        # Ver figura 22 na folha de especificações: Mapa do registrador BootLoader
        # Verifica registrador HW_ID (0x20) - valor correto 0x81
        hardware_id = self.i2c.readfrom_mem(self.addr, 0x20, 1)
        if (hardware_id[0] != 0x81):
            raise ValueError('Hardware ID errado. Wrong Hardware ID.')
        # Verifica registrador de Estado (0x00) para saber se uma aplicação válida está presente
        status = self.i2c.readfrom_mem(self.addr, 0x00, 1)
        # Ver figura 12 na folha de especificações: Registrador de Estado: bit 4: App válido
        if not (status[0] >> 4) & 0x01:
            raise ValueError('Aplicação inválida.')
        # Início da aplicação. Escrita sem dados para App_Start (0xF4)   
        self.i2c.writeto(self.addr, bytearray([0xF4]))
        # Modo de direção 1 - Ver figura 13 na folha de especificações: Registrador de Modo de Medida (0x01) 
        self.i2c.writeto_mem(self.addr, 0x01, bytearray([0b00011000]))

    def data_ready(self):
        # Retorna verdadeiro se novos dados foram descarregados. Valores em .eCO2 e .tVOC
        status = self.i2c.readfrom_mem(self.addr, 0x00, 1)
        # bit 3 no registrador de Estado: data_ready
        if (status[0] >> 3) & 0x01:
        # Ver figura 14 na folha de especificações: Registrador algoritmo Byte Order (0x02)
            register = self.i2c.readfrom_mem(self.addr, 0x02, 4)
            co2HB = register[0]
            co2LB = register[1]
            tVOCHB = register[2]
            tVOCLB = register[3]
            self.eCO2 = ((co2HB << 8) | co2LB)
            self.tVOC = ((tVOCHB << 8) | tVOCLB)
            return True
        else:
            return False
