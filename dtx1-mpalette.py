# Script for extracting raw image from old DTX v1 format which don't have color list at all and uses master palette instead
# Usage:
# python.exe dtx1-mpalette.py --input CRATE1.dtx --output CRATE1.raw
# To convert raw pixels you got from script use ImageMagick with command:
# convert.exe -size 128x128 -depth 8 gray:CRATE1.raw CRATE1.png
# Just remember to use your image size from real file, not from example

import argparse
import sys
import struct
import io
import os
from enum import Enum

# Setting all the available arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Path and filename of the input DTX v1 with master palette to read from")
parser.add_argument("-o","--output", help="Path and filename of the output RAW image")
args = parser.parse_args()

# Reading header of the file. Thanks to Amphos
class DtxHeader(object):
    # don't think I need it anymore
    def __init__(self): # called on creation, set up some sane defaults
        self.a0 = 4
        self.b0 = 8

    # Parsing the header for DTX v1
    def parsev1(self, bytes_):
        self.a0 = int.from_bytes(bytes_.read(2), 'little', signed=True)
        self.b0 = int.from_bytes(bytes_.read(2), 'little', signed=True)
        self.a1 = int.from_bytes(bytes_.read(4), 'little', signed=True)
        self.b1 = int.from_bytes(bytes_.read(4), 'little', signed=True)
        self.c1 = int.from_bytes(bytes_.read(4), 'little', signed=True)
        self.unk = int.from_bytes(bytes_.read(2), 'little', signed=True)
        self.width = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.height = int.from_bytes(bytes_.read(2), 'little', signed=False)

# Reading input file
input_file=open(args.input, 'rb')

# Reading header like a stream of bytes and parsing
header = DtxHeader()
header.parsev1(io.BytesIO(input_file.read()))

# Checking if the arguments are correct
if not args.input or not args.output:
    print("You need to specify both input and output files")
    exit()

# We will not check any header information so be careful and be sure this is proper format

# Extracting raw data from first mipmap of the file
# Opening output file to write to
output_file=open(args.output, 'wb')

# Calculating image data size (1st mipmap)
image_size = int(header.width * header.height)

# Setting offset to 22nd byte (beginning of pixels data)
input_file.seek(22)
   
# Let's read the pixel data byte by byte
for i in range(image_size):
    output_file.write(input_file.read(1))

# Closing output file
output_file.close()

# Closing input file
input_file.close()