
import numpy as np
from gnuradio import gr

class blk(gr.sync_block):  
    """Bloque de Python Embebido - Lee la información de la tabla PMT y el descriptor de emergencia."""

    def _init_(self):  
        """Inicialización del bloque"""
        gr.sync_block._init_(
            self,
            name='Read_PMT', 
            in_sig=[np.ubyte],  
            out_sig=[np.ubyte]  
        )

    # ---------- Función que convierte de Binario a Decimal ---------
    def binario_a_decimal(self, binario):
        bits = list(binario)
        valor = 0

        for i in range(len(bits)):
            bit = bits.pop()  
            if bit == '1':
                valor += pow(2, i)  
        return valor

    # --------- Función que convierte de Decimal a Binario de 8 bits -----------
    def decimal_a_binario(self, decimal):
        "
        if decimal <= 0:
            return "00000000"
        binario = ""
        while decimal > 0:
            residuo = int(decimal % 2)  
            decimal = int(decimal / 2) 
            binario = str(residuo) + binario  

        binario = binario.zfill(8)  
        return binario

    # ---------- Función para determinar el Tipo de Stream -----------
    def StreamType(self, ID_ts_d):
        """Determina el tipo de stream basado en el ID"""
        if ID_ts_d == 0:
            mensaje_TS = 'No definido'
        elif ID_ts_d == 1:
            mensaje_TS = 'Video Conforme ISO/IEC 111722-2'
        elif ID_ts_d == 2:
            mensaje_TS = 'Video Conforme ITU Recommendation H.262'
        elif ID_ts_d == 3:
            mensaje_TS = 'Audio Conforme ISO/EC 11172-3'
        elif ID_ts_d == 4:
            mensaje_TS = 'Audio Conforme ISO/EC 13818-3'
        elif ID_ts_d == 5:
            mensaje_TS = 'Sección'
        elif ID_ts_d == 6:
            mensaje_TS = 'Paquetes PES'
        elif ID_ts_d == 7:
            mensaje_TS = 'MHEG conforme ISO/IEC 13522-5'
        elif ID_ts_d == 8:
            mensaje_TS = 'Conforme ITU Recomendation H222.0:2002, Anexo'
        elif ID_ts_d == 9:
            mensaje_TS = 'Conforme ITU Recomendation H222.1'
        elif ID_ts_d == 10:
            mensaje_TS = 'Conforme ISO/IEC 13818-6 (tipo A)'
        elif ID_ts_d == 11:
            mensaje_TS = 'Conforme ISO/IEC 13818-6 (tipo B)'
        elif ID_ts_d == 12:
            mensaje_TS = 'Conforme ISO/IEC 13818-6 (tipo C)'
        elif ID_ts_d == 13:
            mensaje_TS = 'Conforme ISO/IEC 13818-6 (tipo D)'
        elif ID_ts_d == 14:
            mensaje_TS = 'Conforme ITU Recomendation H222.0 auxiliary data'
        elif ID_ts_d == 15:
            mensaje_TS = 'Audio conforme  ISO/IEC 13818-7 (ADTS transport syntax)'
        elif ID_ts_d == 16:
            mensaje_TS = 'Audio conforme  ISO/IEC 14496-2'
        elif ID_ts_d == 17:
            mensaje_TS = 'Audio conforme  ISO/IEC 14496-3'
        elif ID_ts_d == 18:
            mensaje_TS = 'Conforme  ISO/IEC 14496-1 SL (flujo de paquetes o flujo de FlexMux transportada en los paquetes de PES)'
        elif ID_ts_d == 19:
            mensaje_TS = 'Conforme ISO/IEC 14496-1 SL (flujo de paquetes o flujo de FlexMux transportado en la ISO/IEC 14496)'
        elif ID_ts_d == 20:
            mensaje_TS = 'Protocolo de sincronización de descarga conforme ISO/IEC 13818-6'
        elif ID_ts_d == 21:
            mensaje_TS = 'Metadata transportada por un paquete PES'
        elif ID_ts_d == 22:
            mensaje_TS = 'Metadata transportada por un metadata_sections'
        elif ID_ts_d == 23:
            mensaje_TS = 'Metadata transportada por el carrusel de datos ISO/IEC 13818-6'
        elif ID_ts_d == 24:
            mensaje_TS = 'Metadata transportada por el carrusel de objetos ISO/IEC 13818-6'
        elif ID_ts_d == 25:
            mensaje_TS = 'Metadata transportada por un protocolo de descarga sincronizado ISO/IEC 13818-6'
        elif ID_ts_d == 26:
            mensaje_TS = 'IPMP stream especificado en la ISO/IEC 13818-11'
        elif ID_ts_d == 27:
            mensaje_TS = 'Video conforme ITU Recommendation H.264 e ISO/IEC 14496-10'
        elif (ID_ts_d >= 28) and (ID_ts_d <= 125):
            mensaje_TS = 'No definido'
        elif ID_ts_d == 126:
            mensaje_TS = 'Data pipe'
        elif ID_ts_d == 127:
            mensaje_TS = 'IPMP stream'
        elif (ID_ts_d >= 128) and (ID_ts_d <= 255):
            mensaje_TS = 'Uso privado'
        else:
            mensaje_TS = ''

        return mensaje_TS

    def work(self, input_items, output_items):
        
        output_items[0][:] = input_items[0]  

        # Extracción de PID de los bytes 1 y 2
        pid11 = self.decimal_a_binario(input_items[0][1])
        pid22 = self.decimal_a_binario(input_items[0][2])
        pid0 = pid11 + pid22  
        pid_b131 = pid0[3:len(pid0)]  
        pid_d131 = self.binario_a_decimal(pid_b131)  

        # Verifica si la tabla es PMT
        if input_items[0][5] == 2 and input_items[0][4] == 0:
            print "\n"
            print "--------------------------------------------------------------------"
            print('PMT PARA SERVICIO DE CAP')
            print "--------------------------------------------------------------------"

            # Re-extrae y muestra el PID
            pid1 = self.decimal_a_binario(input_items[0][1])
            pid2 = self.decimal_a_binario(input_items[0][2])
            pid = pid1 + pid2
            pid_b13 = pid[3:len(pid)]
            pid_d13 = self.binario_a_decimal(pid_b13)
            print "PID:", pid_d13, "y en hex:", hex(pid_d13)

            # Extrae la longitud de la sección
            section_len1 = self.decimal_a_binario(input_items[0][6])
            section_len2 = self.decimal_a_binario(input_items[0][7])
            section_length = section_len1 + section_len2 
            section_length_12b = section_length[4:len(section_length)]  
            section_length_12d = self.binario_a_decimal(section_length_12b)
            print "Longitud de la sección:", section_length_12d, "y en hex:", hex(section_length_12d)

            
            section_sid = section_length[0]
            print "Error de sintaxis de sección:", section_sid, "entonces", section_sid == '1'

            # Extrae los datos de la PMT 
            longitud = section_length_12d
            trama_pmt = input_items[0][5:longitud + 8]

            # Extrae y muestra el CRC-32 (últimos 4 bytes)
            tam_trama_pmt = len(trama_pmt)
            CRC_32_list = trama_pmt[-4:tam_trama_pmt]
            print "CRC-32:", CRC_32_list

            # Extrae el número de programa
            program_num1 = self.decimal_a_binario(trama_pmt[3])
            program_num2 = self.decimal_a_binario(trama_pmt[4])
            program_number = program_num1 + program_num2
            program_number_d = self.binario_a_decimal(program_number)
            print "Número de programa:", program_number_d, "y en hex:", hex(program_number_d)

            # Extrae el número de versión
            byte5 = trama_pmt[5]
