************ Receiving metadata from a football match on DTT *********************

******Description of the files

*** Block_ReadPMT
The file shows the code applied in the block diagram of GNU radio, this block
fulfills the function of verifying the information that is had in the reception as well as voice,
video and data.

*** DTT_Metadata_Reception
The file presents the code which allows generating the graphical interface that
allows us to obtain the information of the metadata of the received signal, additionally it sends the
metadata obtained to the arduino with which the LEDs are turned on as presented in the
article.

*** Tests_Leds
This file contains the code that allows the LEDs to be turned on depending on the different positions obtained with the information from the received metadata.