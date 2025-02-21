import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import numpy as np
import shutil
import webbrowser
import socket

# Función para determinar la IP que tiene el equipo al conectarse a una red de internet
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No es necesario que sea alcanzable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

global ip_local
ip_local = get_ip()

# Función para abrir reproductor DASH alojado en el servidor web HTTP
def abrir_reproductor_DASH():
    url = f'http://{ip_local}/FutbolMpegDash/admin.html'  # URL predeterminada
    webbrowser.open(url)

# Función para codificar el video a distintas resoluciones y tasa de bits con FFmpeg
def codificar_video (input_file, output_file, resolution, bitrate):
    cmd = [
        'ffmpeg', '-y', '-i', input_file, '-s', resolution, '-c:v', 'libx264', '-b:v', bitrate, '-g', '90', '-an',
        output_file
    ]
    subprocess.run(cmd)

# Función para codificar el audio del video a 192 kbps con FFmpeg
def codificar_audio (input_file, output_file):
    cmd = [
        'ffmpeg', '-y', '-i', input_file, '-c:a', 'aac', '-b:a', '192k', '-vn', output_file
    ]
    subprocess.run(cmd)

# Función para generar el manifiesto MPD con la herramienta MP4Box
''' Función para convertir lo archivos de video y audio compatibles al estandar MPEG-DASH. 
    Además, se genera el manifiesto MPD que permite la reproducción del contenido multimedia
     de forma adaptativa. '''
def crear_manifiesto_mpd():
    cmd = [
        'MP4Box', '-dash', '5000', '-rap', '-frag-rap', '-profile', 'dashavc264:onDemand',
        'video_256x144.mp4', 'video_640x360.mp4', 'video_1280x720.mp4', 'video_audio_192k.m4a',
        '-out', 'manifiesto.mpd'
    ]
    subprocess.run(cmd)

# Función para copiar los archivos necesarioas al directorio virtual
def copiar_archivo(origen, destino):
    try:
        shutil.copy2(origen, destino)
        print(f"Archivo copiado de '{origen}' a '{destino}'")
    except FileNotFoundError:
        print(f"El archivo '{origen}' no existe o no se puede acceder.")

# Funcion para pasar un número binario a decimal
def binario_a_decimal(binario):
    if len(binario.shape) == 1:
        f = 1
        c = len(binario)
        binario = binario.reshape((1, c))
    else:
        f, c = binario.shape
    decimal = np.zeros(f)
    for i in range(f):
        sum = 0
        x = 0
        for j in range(c-1, -1, -1):
            if binario[i,j] == 1:
                sum += 2**x
            decimal[i] = sum
            x += 1
    return decimal

# Funcion para pasar un número decimal a binario
def decimal_a_binario(decimal, nbits):
    bin = np.zeros((len(decimal), nbits))
    for i in range(len(decimal)):
        x = nbits - 1
        for j in range(nbits):
            bin[i, x] = decimal[i] % 2
            decimal[i] = decimal[i] // 2
            x -= 1
    return bin

# Función para identificar el PID de los paquetes de audio, video y datos
def TS_PID(trama):
    bytes_trama = [trama[1], trama[2]] # Extraemos los valores que se contienen en la posición 2 (índice 1) y 3 (índice 2)
    bin = decimal_a_binario(bytes_trama, 8) # Convertimos a binario de 8 bits ambos valores
    bin = bin.reshape(1, 2*8)[0] # Ambos valores en binarios se ordenan en uno solo (16 bits)
    PID_bits = bin[3:] # Se excluyen los 3 bits mas significativos

    PIDd = binario_a_decimal(PID_bits) # Obtenemos el valor binario a decimal siendo este el valor de PID

    return PIDd

# Función para dirigirme a la pagina web donde se encuentra el contenido multimedia a reproducir
def ir_al_sitio_web():
    url = f'http://{ip_local}/FutbolMpegDash/admin.html'  # URL predeterminada
    webbrowser.open(url)

# Función para seleccionar la opción de inicio
def seleccionar_opcion(opcion):
    if opcion == "Nuevo TS":
        boton_seleccionar.config(state="normal")
        boton_ir_sitio_web.config(state="disabled")
    elif opcion == "TS existente":
        boton_seleccionar.config(state="disabled")
        boton_ir_sitio_web.config(state="normal")

# Función para seleccionar el TS que recibe el equipo receptor
def seleccionar_TS():
    global nombre  # Declarar la variable como global para que esté disponible en otras funciones
    archivo = filedialog.askopenfilename(filetypes=[("Archivos TS", "*.ts")]) # Solo detecta la extensión .ts
    if archivo:
        nombre_archivo.set(os.path.basename(archivo))  # Se obtiene el nombre del archivo
        boton_preparation.config(state="normal")  # Habilita el botón para preparar la transmisión
        nombre = archivo  # Almacena el nombre del archivo en la variable global 'nombre'
        
# Función donde se realiza el proceso de demultiplexación y decodificación de audio video y datos
def preparar_transmision():

    archivo = open(nombre, 'rb') # Se importa el TS detectado en modo de lectura binaria

    # Se determina el numero de paquetes que contiene el archivo .ts recibido
    D = os.stat(nombre) # Se obtiene información general del TS
    nbytes = D.st_size # Se extrae el numero total de bytes del TS
    valor = 188 # Numero de bytes que tiene cada paquete
    paquetes = int(nbytes / valor) # Se calcula el número total de paquetes

    ''' -------------------------------------- DEMULTIPLEXACIÓN --------------------------------------------- '''

    # Lista para almacenar los paquetes con PID 256 y 257
    paquetes_pid_2065_2075 = [] # --> Para video y audio
    paquetes_pid_2085 = [] # --> Para datos

    # Trama de los paquetes
    # Se determina el valor del PID tanto para video como para audio, para proceder con 
    # la demultiplexación del contenido del TS recibido. 
    for i in range(paquetes):
        rango = i * valor # Se indica que cada trama tiene un tamaño de 188
        archivo.seek(rango, os.SEEK_SET) # Indicamos que cada trama del TS debe ser de una longitud de 188 
        trama = archivo.read(valor) # Loa valores del paquete se almacenan en la variable trama
        PIDd = TS_PID(trama) # Se extrae el identificador PID del paquete en formato decimal

        # Almacenamos las tramas que contengan el valor de PID de video y audio en uno solo, y datos en otro
        if PIDd == 2085: # --> Para datos
            paquetes_pid_2085.append(trama)
        else:
            paquetes_pid_2065_2075.append(trama)
        
    ''' Una vez que separamos los contenidos del TS, se procede a guardarlos en archivos 
    TS nuevos. '''
    # Nombre del nuevo archivo para video y audio
    nuevo_video = 'videoTS_demux.ts'
    nuevo_datos = 'datosTS_demux.ts'

    # Abrir el nuevo archivo en modo de escritura binaria
    with open(nuevo_video, 'wb') as nuevo_archivo:
        # Escribir las tramas de los paquetes_pid_2065_2075 en nuevoArchivo
        for trama in paquetes_pid_2065_2075:
            nuevo_archivo.write(trama)

    # Abrir el nuevo archivo en modo de escritura binaria
    with open(nuevo_datos, 'wb') as nuevo_archivo:
        # Escribir las tramas de los paquetes_pid_2085 en nuevoArchivo
        for trama in paquetes_pid_2085:
            nuevo_archivo.write(trama)

    '''-------------------------------- DECODIFICACIÓN DE AUDO Y VIDEO -----------------------'''

    # Generamos un vector con la lista de resoluciones y bitrates que tendra el contenido multimedia
    resolutions = [('256x144', '250k'), ('640x360', '1200k'), ('1280x720', '2400k')]

    # Itera sobre las resoluciones y tasas de bits
    for resolution, bitrate in resolutions:
        output_filename = f'video_{resolution}.mp4'
        # Se realiza la codificacion del video usando FFmpeg con la funcion codificar_video
        codificar_video(nuevo_video, output_filename, resolution, bitrate) 


    # Se realiza la codificacion del audio usando FFmpeg con la funcion codificar_video
    codificar_audio(nuevo_video, 'video_audio_192k.m4a')

    '''---------------------------------- DECODIFICACIÓN DE LOS DATOS ------------------------------------------'''

    # Se crea un vector para almacenar los valores extraídos de cada posición del balón dentro de la cancha de fútbol
    vector_coordenada = []

    # Las tramas contenidas en paquetes_pid_2085 se iteran para extraer el valor requerido
    for trama in paquetes_pid_2085:
        # Extraer el valor de la posición 5 (índice 4) de la trama
        valor_extraido = trama[4]
        vector_coordenada.append(valor_extraido) # Almacenamos el valor extradio al final del vector generado

    # Se genera un archivo .txt donde se guardan las posiciones del balón
    nombre_archivo = 'Coordenadas.txt'

    # Se abre el archivo .txt en modo de escritura
    with open(nombre_archivo, 'w') as archivo_txt:
        # Se itera el vector_coordenadas para pasar cada valor que contiene al archivo .txt
        for valor in vector_coordenada:
            archivo_txt.write(f"{valor}\n") 

    
    '''--------------------------------------- GENERACIÓN DE FICHERO MPD ---------------------------------------'''

    # Se genera el manifiesto MPD con la función crear_manifiesto_mpd, donde tambien se obtienen archivos de
    # inicialización compatibles con el estandar MPEG-DASH
    crear_manifiesto_mpd()

    '''-------------------------------------- SUBIR ARCHIVOS AL SERVIDOR WEB -----------------------------------'''

    cuadro_mensaje.delete(1.0, tk.END)  # Borra el contenido anterior del cuadro de texto (PARA LA INTERFAZ)
    cuadro_mensaje.insert(tk.END, "Completado... Listo para reproducir") # Mensaje de proceso completado
    
    # Ruta de la carpeta donde se encuentran los archivos
    ruta_carpeta = "./" # Indica que los archivos se encuentran en el mismo lugar que el codigo .py

    # Se realiza la lista de archivos .mp4 .m4a y .txt generados que se presentan en la Interfaz
    archivos_mp4_m4a_mpd = [archivo for archivo in os.listdir(ruta_carpeta) if archivo.lower().endswith((".mpd", 
                                                                                                         ".txt", 
                                                                                                         ".mp4", 
                                                                                                         ".m4a",))]

    # Insertar los nombres de los archivos en el cuadro de texto
    for nombre_archivo in archivos_mp4_m4a_mpd:
        cuadro_archivos_mp4_m4a_mpd.insert(tk.END, nombre_archivo + "\n")

    # Ahora se suben los archivos generados al servidor web por medio del directorio virtual creado
    # Ruta de la carpeta donde se encuentra el script
    carpeta_origen = os.path.dirname(os.path.abspath(__file__))

    # Ruta de la carpeta de destino (Directorio virutal)
    carpeta_destino = 'C:\\Program Files\\FutbolMpegDash\\admin' # Se copian en la carpeta admin del directorio virtual

    # Lista de archivos que se copian al directorio virtual
    archivos = ['video_256x144_dashinit.mp4', 'video_640x360_dashinit.mp4', 'video_1280x720_dashinit.mp4', 
                'video_audio_192k_dashinit.mp4', 'manifiesto.mpd']

    # Copiar cada archivo a la carpeta admin del directorio virtual
    for nombre_archivo in archivos:
        ruta_archivo_origen = os.path.join(carpeta_origen, nombre_archivo)
        ruta_archivo_destino = os.path.join(carpeta_destino, nombre_archivo)
        
        # Verificar si el archivo existe antes de copiarlo
        if os.path.exists(ruta_archivo_origen):
            shutil.copy(ruta_archivo_origen, ruta_archivo_destino)
            print(f'Archivo {nombre_archivo} copiado a {ruta_archivo_destino}')
        else:
            print(f'El archivo {nombre_archivo} no existe en la carpeta de origen')


    # Se copia el archivo .txt al directorio virtual para mostrar las posiciones del balon mientras se reproduce
    # el contenido multimedia.
    archivo_origen = "Coordenadas.txt"
    carpeta_destino = "C:\\Program Files\\FutbolMpegDash\\radar" # Se copian en la carpeta radar del directorio virtual
    copiar_archivo(archivo_origen, carpeta_destino) # Se emplea la función copiar_archivo

    global ip_local # Se declara la variable ip_local como global para usar en todo el código
    ip_local = get_ip() # Se obtiene la IP que tiene el equipo al conectarse a una red de internet

        
    # Mensaje que indica que todo esta listo para tranmisitr
    cuadro_texto.delete(1.0, tk.END)  # Borra el contenido anterior del cuadro de texto
    cuadro_texto.insert(tk.END, "Archivos generados correctamente y subidos al servidor.") # Mensaje de exito

    boton_reproducir.config(state="normal")  # Habilita el botón de transmisión

'''--------------------------- CREACIÓN DE LA INTERFAZ GRÁFICA "RECEPTOR MPEG DASH" ---------------------------- '''
    
# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Receptor MPEG DASH") # Nombre de la ventana de la interfaz

ventana.configure(bg="white")  # Para cambiar el color de fondo de la ventana
bg_image = tk.PhotoImage(file="futbol.png") # Para agregar una imagen de fondo

# Se crear una etiqueta para la imagen de fondo para manipularla como se desee
bg_label = tk.Label(ventana, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

ventana.geometry("750x340") # Tamaño específico para la ventana
ventana.resizable(width=False, height=False) # Para que la ventana no sea redimensionable

# Se indica el Título de la interfaz en formato centrado
titulo = tk.Label(ventana, text="RECEPTOR MPEG DASH", font=("Helvetica", 16, "bold"), bg="white")
titulo.pack(pady=10) # Tamaño del menu de selección

# Se genera el menú de seleccion de opciones para escoger la acción a realizar con la interfaz
opciones = ["Nuevo TS", "TS existente"]
opcion_seleccionada = tk.StringVar()
opcion_seleccionada.set(opciones[0])  # Opción predeterminada
menu = tk.OptionMenu(ventana, opcion_seleccionada, *opciones, command=seleccionar_opcion)
menu.pack(anchor="w", padx=10)

menu.place(x=325, y=menu.winfo_height() + 45) # Se ajusta la posicion del menu de selección

boton_ir_sitio_web = tk.Button(ventana, text="Ir al sitio web", command=ir_al_sitio_web) # Botón para acceder a la pagina web sin realizar el proceso
boton_ir_sitio_web.pack(anchor="w", padx=10) # Tamaño del boton
boton_ir_sitio_web.config(state="disabled")  # Botón inicialmente deshabilitado

boton_ir_sitio_web.place(x=600, y=boton_ir_sitio_web.winfo_height() + 45) # Se ajusta la posicion del boton Ir al sitio web

# Crea un botón para seleccionar el archivo (alineado a la izquierda)
boton_seleccionar = tk.Button(ventana, text="Seleccionar TS", command=seleccionar_TS)
boton_seleccionar.pack(anchor="w", padx=10) # Tamaño del botón

boton_seleccionar.place(x=10, y=boton_seleccionar.winfo_height() + 85) # Se ajusta la posicion del botón Seleccionar TS

nombre_archivo = tk.StringVar()# Variable StringVar para almacenar el nombre del archivo

# Se crea un cuadro de texto para mostrar el nombre del archivo
etiqueta_nombre = tk.Entry(ventana, textvariable=nombre_archivo, bg="lightgray") # Características del cuadro de texto
etiqueta_nombre.pack(anchor="w", padx=10) # Tamaño del cuadro de texto

etiqueta_nombre.place(x=110, y=etiqueta_nombre.winfo_height() + 88) # Se ajusta la posición del cuadro de texto

# Se crea el botón para "Preparar Transmisión" (inicialmente desactivado)
boton_preparation = tk.Button(ventana, text="Preparar Transmisión", state="disabled", command=preparar_transmision)
boton_preparation.pack(anchor="w", pady=10) # Tamaño del botón

boton_preparation.place(x=10, y=etiqueta_nombre.winfo_height() + 120) # Se ajusta la posición del botón Preparar Transmisión

# Se crea un cuadro de texto para mostrar el mensaje de progreso
cuadro_mensaje = tk.Text(ventana, height=1, width=40, bg="lightgray") # Características del cuadro de texto
cuadro_mensaje.pack(anchor="w", padx=10) # Tamaño del cuadro de texto

cuadro_mensaje.place(x=10, y=etiqueta_nombre.winfo_height() + 150)  # Se ajusta la posición del cuadro de texto

# Se crea una etiqueta para el subtítulo Archivos generados
etiqueta_subtitulo = tk.Label(ventana, text="Archivos generados", bg="white") # Subtitulo con fondo blanco
etiqueta_subtitulo.pack(anchor="w", padx=10) # Tamaño del subtítulo

etiqueta_subtitulo.place(x=370, y=etiqueta_nombre.winfo_height() + 85) # Se ajusta la posición del subtítulo

# Se crea un cuadro de texto para mostrar los archivos .mp4 .m4a, .txt y .mpd generados
cuadro_archivos_mp4_m4a_mpd = tk.Text(ventana, height=10, width=40, bg="lightgray") # Características del cuadro de texto
cuadro_archivos_mp4_m4a_mpd.pack(anchor="w", padx=10) # Tamaño del cuadro de texto

cuadro_archivos_mp4_m4a_mpd.place(x=370, y=etiqueta_nombre.winfo_height() + 105) # Se ajusta la posición del cuadro de texto

# Se crea una etiqueta para el subtítulo Estadp
etiqueta_subtitulo2 = tk.Label(ventana, text="Estado", bg="white") # Subtitulo con fondo blanco
etiqueta_subtitulo2.pack(anchor="w", padx=10) # Tamaño del subtítulo

etiqueta_subtitulo2.place(x=10, y=etiqueta_nombre.winfo_height() + 180) # Se ajusta la posición del subtítulo

# Se crea un cuadro de texto para mensaje final
cuadro_texto = tk.Text(ventana, height=3, width=40, bg="lightgray") # Características del cuadro de texto
cuadro_texto.pack(padx=10) # Tamaño del cuadro de texto

cuadro_texto.place(x=10, y=etiqueta_nombre.winfo_height() + 200) # Se ajusta la posición del cuadro de texto

# Se crea un botón para "Reproducir" (inicialmente desactivado)
boton_reproducir = tk.Button(ventana, text="Reproducir", state="disabled", command=abrir_reproductor_DASH)
boton_reproducir.pack()

# Ajusta la posición del botón
boton_reproducir.place(x=325, y=etiqueta_nombre.winfo_height() + 285)  # Se ajusta la posición del botón Reproducir

# Se inicia la interfaz gráfica
ventana.mainloop()