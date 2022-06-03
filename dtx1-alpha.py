# Script for extracting alpha raw image from DTX v1

import argparse
import sys
import struct
import io
import os
from enum import Enum

# Setting all the available arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Path and file name of the input DTX to read meta from")
parser.add_argument("-o","--output", help="Path and file name of the output DTX to transfer meta to")
args = parser.parse_args()

# Defining DTX version enumeration values
class DTX_ver_Enum(Enum):
    DTX_VERSION_LT1  = -2
    DTX_VERSION_LT15 = -3
    DTX_VERSION_LT2  = -5

# Reading header of the file. Thanks to Amphos
class DtxHeader(object):
    def __init__(self): # called on creation, set up some sane defaults
        self.filetype = 0
        self.version = -5
        self.width = -1
        self.height = -1
        self.mipmaps = 4

    # Parsing the header for DTX v1
    def parsev1(self, bytes_):
        self.filetype = int.from_bytes(bytes_.read(4), 'little', signed=False)
        self.version = int.from_bytes(bytes_.read(4), 'little', signed=True)
        self.width = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.height = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.mipmaps_default = int.from_bytes(bytes_.read(2), 'little', signed=False)   # always 4
        self.light_flag = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.dtx_flags = "{:08b}".format(int.from_bytes(bytes_.read(1), 'little', signed=False)) + "{:08b}".format(int.from_bytes(bytes_.read(1), 'little', signed=False))
        # Bit Flags for DTX Flags
        self.DTX_DONT_MAP_MASTER="DTX_DONT_MAP_MASTER " if int(self.dtx_flags[2]) else ""
        self.DTX_SECTIONSFIXED="DTX_SECTIONSFIXED " if int(self.dtx_flags[4]) else ""
        self.DTX_ALPHA_MASK="DTX_ALPHA_MASK " if int(self.dtx_flags[6]) else ""
        self.DTX_FULLBRITE="DTX_FULLBRITE " if int(self.dtx_flags[7]) else ""

# Reading input file
input_file=open(args.input, 'rb')

# Reading header like a stream of bytes and parsing
header = DtxHeader()
header.parsev1(io.BytesIO(input_file.read()))

# Dealing with errors of wrong file type or wrong DTX version
if header.filetype != 0:
    print("Wrong file type, not a DTX texture")
    exit()

# In NOLF there is BARON_ACTION.DTX file with mess in DTX version, but overall it's compatible file for DTX_VERSION_LT2.
if header.filetype == 0 and header.version != -5 and header.version != -3 and header.version != -2:
    print("Wrong/Broken DTX version (not -2 or -3 or -5). If you sure it's compatible DTX file (NOLF1 had such BARON_ACTION.DTX for example),")
    print("you can edit your file in HEX editor replacing 8 bytes at the start of the file by this:")
    print("DTX v1:   00 00 00 00 FE FF FF FF")
    print("DTX v1.5: 00 00 00 00 FD FF FF FF")
    print("DTX v2:   00 00 00 00 FB FF FF FF")
    exit()

if header.filetype == 0 and header.version != -2:
    print("Wrong DTX version: {} ({}). Script is intended to work only with -2 (DTX_VERSION_LT1)".format(header.version, DTX_ver_Enum(header.version).name))
    exit()

# Transfering meta information between the files for DTX v2
#if args.output and header.version == -2:
if header.version == -2:
    # Opening output file to write to
    output_file=open(args.output, 'wb')
    mipmap_size = int(header.width * header.height + header.width/2 * header.height/2 + header.width/4 * header.height/4 + header.width/8 * header.height/8)
    alpha_size = int((header.width * header.height) / 2)

    # Setting offset to 1068th byte (beginning of image mipmaps)
    input_file.seek(1068+mipmap_size)
    #output_file.seek(12)
    # Writing first 14 bytes till Number of mipmaps used

    # A code for swapping nibbles
    # Let's read the file byte by byte
    for i in range(alpha_size):
        data = input_file.read(1)
        # converting to int
        x = int.from_bytes(data,byteorder='little')
        # swapping nibbles
        x = (x & 0x0F)<<4 | (x & 0xF0)>>4
        # converting back to bytes and writing to file
        output_file.write(x.to_bytes(1, 'little'))

    #output_file.write(input_file.read(alpha_size))
    # Skipping BPP
    #input_file.seek(27)
    #output_file.seek(27)
    # Writing everything else till the end of header
    #output_file.write(input_file.read(137))
    # Closing output file
    #output_file.byteswap(True)
    output_file.close()

# Closing input file
input_file.close()