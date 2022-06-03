# Script for extracting alpha raw image from DTX v1 and swapping nibbles in its bitmap

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

# Checking if the arguments are correct
if not args.input or not args.output:
    print("You need to specify both input and output files")
    exit()

# Dealing with errors of wrong file type
if header.filetype != 0:
    print("Wrong file type, not a DTX texture, first bye isn't 00")
    exit()

# Checking DTX version
if header.filetype == 0 and header.version != -2:
    print("Wrong DTX version: {} ({}). Script is intended to work only with -2 (DTX_VERSION_LT1)".format(header.version, DTX_ver_Enum(header.version).name))
    print("If you are sure it is correct DTX v1 format, you can replace first 8 bytes of the file in HEX editor to:")
    print("DTX v1:   00 00 00 00 FE FF FF FF")
    exit()

# Extracting war data from first mipmap on the alpha image only if we have DTX_ALPHA_MASK flag
if header.version == -2 and header.DTX_ALPHA_MASK:

    # Opening output file to write to
    output_file=open(args.output, 'wb')

    # Calculating image data size (all 4 mipmaps) and alpha data size (1st mipmap)
    mipmap_size = int(header.width * header.height + header.width/2 * header.height/2 + header.width/4 * header.height/4 + header.width/8 * header.height/8)
    alpha_size = int((header.width * header.height) / 2)

    # Setting offset to 1068th byte (beginning of image mipmaps) + size of all image mipmaps to skip this sections to start from alpha
    input_file.seek(1068+mipmap_size)
    
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

    # Closing output file
    output_file.close()

# Closing input file
input_file.close()