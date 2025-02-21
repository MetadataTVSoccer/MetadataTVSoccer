------------------------------- PROJECT DESCRIPTION --------------------------------

This repository contains the source code for my thesis, which aims to improve accessibility in the
transmission of sporting events for visually impaired people. To do this, a system has been developed that
multiplexes metadata into a transport stream (TS) along with audio and video, allowing
real-time synchronization of the ball's position with a haptic device.

1. Generation of the Transport Stream (TS)

-A video and audio file is taken.
-A metadata file is generated with the coordinates of the ball on the field, sampled every 0.5 seconds.
-The metadata is multiplexed with the video and audio into a single transport stream.

2. Structure of the Metadata Packet

Byte 1: Synchronization byte.
Byte 2-3: Packet identifier (PID).
Byte 4: Continuity byte.
Byte 5: Ball coordinate.