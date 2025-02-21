------------------------------- DESCRIPCIÓN DEL PROYECTO --------------------------------

Este repositorio contiene el código fuente de mi tesis, cuyo objetivo es mejorar la accesibilidad en la 
transmisión de eventos deportivos para personas con discapacidad visual. Para ello, se ha desarrollado un 
sistema que multiplexa metadatos en un flujo de transporte (TS) junto con audio y video, permitiendo la 
sincronización en tiempo real de la posición del balón con un dispositivo háptico.

1. Generación del Stream de Transporte (TS)

	-Se toma un archivo de video y audio.
	-Se genera un archivo de metadatos con las coordenadas del balón en el campo, muestreadas cada 0.5 segundos.
	-Se multiplexan los metadatos con el video y audio en un solo flujo de transporte.

2. Estructura del Paquete de Metadatos

	Byte 1: Byte de sincronización.
	Byte 2-3: Identificador de paquete (PID).
	Byte 4: Byte de continuidad.
	Byte 5: Coordenada del balón.
