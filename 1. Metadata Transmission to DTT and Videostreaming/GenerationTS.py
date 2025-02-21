#!/usr/bin/env python
#coding: utf8

# ********* Librerías a utilizar *********
import os
from dvbobjects.PSI.PAT import *
from dvbobjects.PSI.NIT import *
from dvbobjects.PSI.SDT import *
from dvbobjects.PSI.PMT import *
from dvbobjects.SBTVD.Descriptors import *

# ********* Parámetros de transmisión y servicio *********
tvd_ts_id = 0x073b              # ID de red
tvd_orig_network_id = 0x073b    # ID de red original
ts_freq = 533                   # Frecuencia de transmisión
ts_remote_control_key = 0x05    # Tecla de acceso rápido al canal
tvd_service_id_sd = 0xe760      # ID de servicio de TV digital
tvd_pmt_pid_sd = 1031           # PID de la PMT del servicio

# ****************** Definición Red NIT ******************
nit = network_information_section(
    network_id=tvd_orig_network_id,
    network_descriptor_loop=[
        network_descriptor(network_name="AndresTV"),
        system_management_descriptor(
            broadcasting_flag=0,
            broadcasting_identifier=3,
            additional_broadcasting_identification=0x01,
            additional_identification_bytes=[]
        )
    ],
    transport_stream_loop=[
        transport_stream_loop_item(
            transport_stream_id=tvd_ts_id,
            original_network_id=tvd_orig_network_id,
            transport_descriptor_loop=[
                service_list_descriptor(
                    dvb_service_descriptor_loop=[
                        service_descriptor_loop_item(
                            service_ID=tvd_service_id_sd,
                            service_type=1
                        ),
                    ]
                ),
                terrestrial_delivery_system_descriptor(
                    area_code=1341,
                    guard_interval=0x01,
                    transmission_mode=0x02,
                    frequencies=[
                        tds_frequency_item(freq=ts_freq)
                    ],
                ),
                partial_reception_descriptor(
                    service_ids=[]
                ),
                transport_stream_information_descriptor(
                    remote_control_key_id=ts_remote_control_key,
                    ts_name="CoordenadasTS",
                    transmission_type_loop=[
                        transmission_type_loop_item(
                            transmission_type_info=0x0F,
                            service_id_loop=[
                                service_id_loop_item(
                                    service_id=tvd_service_id_sd
                                ),
                            ]
                        ),
                        transmission_type_loop_item(
                            transmission_type_info=0xAF,
                            service_id_loop=[]
                        ),
                    ]
                ),
            ]
        ),
    ],
    version_number=0,
    section_number=0,
    last_section_number=0,
)

# ****************** Definición servicios SDT ******************
sdt = service_description_section(
    transport_stream_id=tvd_ts_id,
    original_network_id=tvd_orig_network_id,
    service_loop=[
        service_loop_item(
            service_ID=tvd_service_id_sd,
            EIT_schedule_flag=0,
            EIT_present_following_flag=0,
            running_status=4,
            free_CA_mode=0,
            service_descriptor_loop=[
                service_descriptor(
                    service_type=1,
                    service_provider_name="ESPE",
                    service_name="FutbolAccesible"
                ),
            ],
        ),
    ],
    version_number=0,
    section_number=0,
    last_section_number=0,
)

# ****************** TABLA PAT ******************
pat = program_association_section(
    transport_stream_id=tvd_ts_id,
    program_loop=[
        program_loop_item(
            program_number=0,
            PID=16
        ),
        program_loop_item(
            program_number=tvd_service_id_sd,
            PID=tvd_pmt_pid_sd
        ),
    ],
    version_number=0,
    section_number=0,
    last_section_number=0,
)

# ****************** TABLA PMT ******************
pmt_sd = program_map_section(
    program_number=tvd_service_id_sd,
    PCR_PID=2065,
    program_info_descriptor_loop=[],
    stream_loop=[
        stream_loop_item(
            stream_type=2,  # mpeg2 video stream type
            elementary_PID=2065,
            element_info_descriptor_loop=[]
        ),
        stream_loop_item(
            stream_type=3,  # mpeg2 audio stream type
            elementary_PID=2075,
            element_info_descriptor_loop=[]
        ),
        # Añadimos el stream de metadatos
        stream_loop_item(
            stream_type=0x15,  # metadatos
            elementary_PID=2085,
            element_info_descriptor_loop=[]
        ),
    ],
    version_number=0,
    section_number=0,
    last_section_number=0,
)

def create_metadata_ts(metadata_file, video_duration_sec, sample_interval_sec):
    # Lectura el archivo de metadatos
    with open(metadata_file, 'r') as f:
        lines = f.readlines()
        metadatos = [int(line.strip(), 16) for line in lines]

    # Inicializar variables
    packets = []
    pid = 2085  # PID para metadatos
    continuity_counter = 0 # Contador de continuidad 
    num_samples = len(metadatos) # Número de muestras
    total_packets_needed = int(video_duration_sec / sample_interval_sec) * num_samples

    # Se crean paquetes TS con los metadatos específicos
    for i in range(total_packets_needed):
        payload = [metadatos[i % num_samples]]
        adaptation_field_control = 1

        # Se crea un paquete TS de 188 bytes
        packet = bytearray(188)
        packet[0] = 0x47  # Sync byte
        packet[1] = (pid >> 8) & 0x1F
        packet[2] = pid & 0xFF
        packet[3] = (continuity_counter & 0x0F) | (adaptation_field_control << 4)
        continuity_counter = (continuity_counter + 1) % 16

        # Se añade la carga útil (coordenadas) al paquete TS
        packet[4:4 + len(payload)] = payload
        packets.append(packet)

    # Escritura de los paquetes en el archivo "coordenadas.ts"
    with open("./coordenadas.ts", "wb") as f:
        for packet in packets:
            f.write(packet)

# Creación el archivo de metadatos desde coordenadas.txt
video_duration_sec = 120  # Duración del video en segundos
sample_interval_sec = 0.5  # Intervalo de muestreo en segundos
create_metadata_ts("coordenadas.txt", video_duration_sec, sample_interval_sec)

# ****************** Guardar secciones y convertir a TS ******************
out = open("./nit.sec", "wb")
out.write(nit.pack())
out.close()
os.system("sec2ts 16 < ./nit.sec > ./nit.ts")

out = open("./pat.sec", "wb")
out.write(pat.pack())
out.close()
os.system("sec2ts 0 < ./pat.sec > ./pat.ts")

out = open("./sdt.sec", "wb")
out.write(sdt.pack())
out.close()
os.system("sec2ts 17 < ./sdt.sec > ./sdt.ts")

out = open("./pmt_sd.sec", "wb")
out.write(pmt_sd.pack())
out.close()
os.system("sec2ts " + str(tvd_pmt_pid_sd) + " < ./pmt_sd.sec > ./pmt_sd.ts")

