#!/bin/bash
# Original data can be found at 
# https://www.iks.rwth-aachen.de/fileadmin/user_upload/downloads/forschung/tools-downloads/air_database_release_1_4.zip
# But not all IRs are converted to WAV already.
# We copy converted WAV files from NAS instead.

DST=../build/data
SRC=~/SMB/srv-fs-01/database/DBS-Thirdparty/AachenRoomImpulseResponseDatabase-AIR/air_wav
mkdir -p $DST
cp -R $SRC/*.wav $DST/
