********** MPEG-DASH Video Streaming Metadata Reception ***********

There are two files:

- admin.html:

This code was used to develop the web page where the multimedia content (football match) is played, which is synchronized with the radar to determine the position of the ball within the field every 0.5 seconds.

- Mpeg-Dash_Receiver.py:

This code is used to develop the interface to select the Transport Stream to be played. Within it, the process of demultiplexing, decoding, adaptation of the video to the MPEG-DASH standard is carried out and finally the necessary files are uploaded to the local web server created.