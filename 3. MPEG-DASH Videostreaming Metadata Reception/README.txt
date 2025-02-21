********* Recepción Metadatos Videostreaming MPEG-DASH ***********

Se encuentran dos archivos:

- admin.html: Por medio de este código se desarrolló la pagina web donde se reproduce el contenido multimedia (partido de futbol), el mismo que se encuentra sincronizado con el radar para determinar la posición del balón dentro del campo cada 0.5 segundos.

- Receptor_Mpeg_Dash.py: Por medio de este código se desarrollo la interfaz para seleccionar el Transport Stream que se desea reproducir. Dentro del mismo se realiza el proceso de demultiplexación, decodificación, adaptación del video al estándar MPEG-DASH y finalmente subir los archivos necesarios al servidor web local creado.