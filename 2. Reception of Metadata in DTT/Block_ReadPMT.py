
import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block - Reading the information from the PMT table and the emergency descriptor.
    Extract the area codes into an Excel file.
    Prints the type of service that contains the superimpose message.
    It receives 188-byte frames that are processed. """

    def __init__(self):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Read_PMT',   # will show up in GRC
            in_sig=[np.ubyte],
            out_sig=[np.ubyte]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        # self.example_param = example_param

    # ---------- Funcion que convierte de Binario a Decimal ---------
    def binario_a_decimal(self, binario):
        # binario = '11111111'
        bits = list(binario)
        valor = 0

        for i in range(len(bits)):
            bit = bits.pop()

            if bit == '1':
                valor += pow(2, i)
        return valor

    # --------- Funcion que convierte de Decimal a Binario -----------
    def decimal_a_binario(self, decimal):
        if decimal <= 0:
            return "00000000"
        # Aqui almacenamos el resultado
        binario = ""
        # Mientras se pueda dividir...
        while decimal > 0:
            # Saber si es 1 o 0
            residuo = int(decimal % 2)
            # E ir dividiendo el decimal
            decimal = int(decimal / 2)
            # Ir agregando el numero (1 o 0) a la izquierda del resultado
            binario = str(residuo) + binario

        binario = binario.zfill(8)
        return binario

    # ---------- Funcion para determinar el Type Stream -----------

    def StreamType(self, ID_ts_d):
        # mensaje_TS = ''

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
            mensaje_TS = 'Seccion'
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
            mensaje_TS = 'Protocolo de sincronizacion de descarga conforme ISO/IEC 13818-6'
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
        """Reading the PMT table"""
        output_items[0][:] = input_items[0]

	pid11 = self.decimal_a_binario(input_items[0][1])
        pid22 = self.decimal_a_binario(input_items[0][2])
        pid0 = pid11 + pid22
        pid_b131 = pid0[3:len(pid0)]
        pid_d131 = self.binario_a_decimal(pid_b131)


	# Identifico tabla PMT
        if input_items[0][5] == 2 and input_items[0][4] == 0:
            #output_items[0] = input_items[0]
            #print(output_items[0])
            print "\n"
            print "--------------------------------------------------------------------"
            print('PMT PARA SERVICIO DE CAP')
  	    print "--------------------------------------------------------------------"
	  
            pid1 = self.decimal_a_binario(input_items[0][1])
            pid2 = self.decimal_a_binario(input_items[0][2])
            pid = pid1 + pid2
            pid_b13 = pid[3:len(pid)]
            pid_d13 = self.binario_a_decimal(pid_b13)
            print "PID:", pid_d13, "y en hex:", hex(pid_d13)

            # --- Section Length ---
            section_len1 = self.decimal_a_binario(input_items[0][6])
            section_len2 = self.decimal_a_binario(input_items[0][7])
            section_length = section_len1 + section_len2
            section_length_12b = section_length[4:len(section_length)]
            section_length_12d = self.binario_a_decimal(section_length_12b)
            print "Section length:", section_length_12d, "y en hex:", hex(section_length_12d)

            # --- Section syntax indicator ---
            section_sid = section_length[0]
            print "Section syntax error:", section_sid, "entonces", section_sid == '1'

            # --- Trama PMT ---
            longitud = section_length_12d
            trama_pmt = input_items[0][5:longitud + 8]
            # print(len(trama_pmt))

            # --- CRC-32 ---
            tam_trama_pmt = len(trama_pmt)
            CRC_32_list = trama_pmt[-4:tam_trama_pmt]
            print "CRC-32:", CRC_32_list

            # --- Broadcasting program number identifier ---
            program_num1 = self.decimal_a_binario(trama_pmt[3])
            program_num2 = self.decimal_a_binario(trama_pmt[4])
            program_number = program_num1 + program_num2
            program_number_d = self.binario_a_decimal(program_number)
            print "Program number:", program_number_d, "y en hex:", hex(program_number_d)

            # --- Version Number ---
            byte5 = trama_pmt[5]
            byte5_b = self.decimal_a_binario(byte5)
            version_number_b = byte5_b[2:7]
            version_number_d = self.binario_a_decimal(version_number_b)
            print "Version Number:", version_number_d, "y en hex:", hex(version_number_d)

            # --- Current next indicator ---
            current_nid = byte5_b[-1]
            print "Current next indicator: ", current_nid, "entonces", current_nid == '1'


            # --- PCR PID ---
            pcr_pid1 = self.decimal_a_binario(input_items[0][13])
            pcr_pid2 = self.decimal_a_binario(input_items[0][14])
            PCR_PID_b = pcr_pid1 + pcr_pid2
            PCR_PID_13b = PCR_PID_b[3:len(PCR_PID_b)]
            PCR_PID_13d = self.binario_a_decimal(PCR_PID_13b)
            print "PCR_PID:", PCR_PID_13d, "y en hex:", hex(PCR_PID_13d)

            # --- Program information length ---
            prog_len1 = self.decimal_a_binario(input_items[0][15])
            prog_len2 = self.decimal_a_binario(input_items[0][16])
            prog_len_b = prog_len1 + prog_len2
            prog_len_b12 = prog_len_b[4:len(prog_len_b)]
            prog_len_d12 = self.binario_a_decimal(prog_len_b12)
            print "Program information length:", prog_len_d12, "y en hex:", hex(prog_len_d12)
            print "--------------------------------------------------------------------"

            prog_comparacion = '000000000000'
            # prog_ewbs = '1111111001000'
            descriptor_ewbs = input_items[0][17]
            # print "DESCRIPTOR EWBS", descriptor_ewbs
            if prog_len_b12 == prog_comparacion:
                # --- Repeat loop ----
                v_loop = input_items[0][17:len(trama_pmt) + 1]  # lista de repeticion
                # v_loop = trama_pmt[12:-4]  # lista de repeticion (Modificamos)
                # print v_loop
                tam_loop = len(v_loop)
                v_loop_bin = ''  # String loop

                # Se concatena en un solo String
                for i in range(tam_loop):
                    v_loop_bin = v_loop_bin + self.decimal_a_binario(v_loop[i])

                tam_vloop = len(v_loop_bin)  # Tamanio del v_loop_bin

                i = 0  # variable iteradora
                ID_TS_d = []
                ES_PID_d = []
                inf_len_ESdv = []
                j = 1  # Variable de information

                while i != tam_vloop:
                    ID_TS = v_loop_bin[i + 0:i + 8]
                    ID_TS_d.append(self.binario_a_decimal(ID_TS))
                    ID_TS_dec = self.binario_a_decimal(ID_TS)
                    print " --------------------- Information", j, "----------------------"
                    print "Stream Type identifier:", ID_TS_dec, "en hex:", hex(ID_TS_dec), ":", self.StreamType(
                        ID_TS_dec)

                    ES_PID = v_loop_bin[i + 11:i + 24]
                    ES_PID_d.append(self.binario_a_decimal(ES_PID))
                    ES_PID_dec = self.binario_a_decimal(ES_PID)
                    print "Elementary Stream PID:", ES_PID_dec, "en hex", hex(ES_PID_dec)

                    inf_len_ES = v_loop_bin[i + 28:i + 40]
                    inf_len_ESdv.append(self.binario_a_decimal(inf_len_ES))
                    inf_len_ESd = self.binario_a_decimal(inf_len_ES)
                    print "ES information length:", inf_len_ESd, "en hex:", hex(inf_len_ESd)

                    cont = (i + 40) + (inf_len_ESd * 8)
                    i = cont
                    j += 1
                    print "----------------------------------------------------------------"

                print "Stream type identifier:", ID_TS_d
                print "Elementary Stream PID:", ES_PID_d
                print "ES information length:", inf_len_ESdv

            
            else:
                 print "\n"

        return len(output_items[0])
        # return 0
