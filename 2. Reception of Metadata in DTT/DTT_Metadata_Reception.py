# -*- coding: utf-8 -*-

# Autor: Luis Gallo

import os

# Función para convertir decimal a binario de 8 bits
def decimal_a_binario(decimal):
    return '{:08b}'.format(decimal)

# Función para convertir binario a decimal
def binario_a_decimal(binario):
    return int(binario, 2)

# Nombre del archivo TS
nombre = 'VideoArgentina.ts'
archivo = open(nombre, 'rb')  # Abrir archivo en modo lectura binaria

# Obtener el tamaño del archivo en bytes
nbytes = os.path.getsize(nombre)
valor = 188
paquetes = nbytes / valor

# Inicializar contador de paquetes con PID 825
contador_825 = 0
datos_pid_825 = []

# Archivo de salida para guardar los datos
outputFile = 'datos_pid_825.txt'
outputID = open(outputFile, 'w')  # Abrir archivo en modo escritura

# Leer todos los paquetes
for n in range(1, int(paquetes) + 1):
    m = n - 1
    rango = m * valor
    archivo.seek(rango)  # Mover el puntero de lectura al inicio del paquete
    trama = archivo.read(valor)  # Leer el paquete completo
    
    # Leer paquetes y encontrar PID
    byte2 = trama[1]
    byte3 = trama[2]
    PID_bits = '{:08b}{:08b}'.format(ord(byte2), ord(byte3))[4:]  # Obtener los últimos 12 bits como PID
    PID_decimal = binario_a_decimal(PID_bits)
    PID_hex = '{:X}'.format(PID_decimal)
    
    # Verificar si el PID es 825
    if PID_hex == '825':
        contador_825 += 1
        
        # Extraer el valor del byte 5 y guardarlo en el archivo
        dato_byte_5 = ord(trama[4])
        datos_pid_825.append(dato_byte_5)
        outputID.write(str(dato_byte_5) + '\n')

# Mostrar el resultado
print('Número de paquetes con PID 825:', contador_825)

# Cerrar archivos
archivo.close()
outputID.close()
