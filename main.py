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
parser.add_argument("-r","--read", help="Option to just read the input file",action="store_true")
parser.add_argument("-t","--table", help="Option to write meta-information in table information to csv file")
args = parser.parse_args()

# Defining BPP enumeration values
class BPP_Enum(Enum):
    BPP_8P = 0
    BPP_8  = 1
    BPP_16 = 2
    BPP_32 = 3
    BPP_S3TC_DXT1 = 4
    BPP_S3TC_DXT3 = 5
    BPP_S3TC_DXT5 = 6
    BPP_32P = 7
    BPP_24  = 8

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

    # Parsing the whole header like a stream of bytes using research for DTX v2
    def parse(self, bytes_):
        self.filetype = int.from_bytes(bytes_.read(4), 'little', signed=False)
        self.version = int.from_bytes(bytes_.read(4), 'little', signed=True)
        self.width = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.height = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.mipmaps_default = int.from_bytes(bytes_.read(2), 'little', signed=False)   # always 4
        self.light_flag = int.from_bytes(bytes_.read(2), 'little', signed=False)

        # Parsing DTX Flags
        self.dtx_flags = "{:08b}".format(int.from_bytes(bytes_.read(1), 'little', signed=False)) + "{:08b}".format(int.from_bytes(bytes_.read(1), 'little', signed=False))
        # Bit Flags for DTX Flags
        self.DTX_PREFER4444="DTX_PREFER4444 " if int(self.dtx_flags[0]) else ""
        self.DTX_NOSYSCACHE="DTX_NOSYSCACHE " if int(self.dtx_flags[1]) else ""
        self.DTX_SECTIONSFIXED="DTX_SECTIONSFIXED " if int(self.dtx_flags[4]) else ""
        self.DTX_MIPSALLOCED="DTX_MIPSALLOCED " if int(self.dtx_flags[5]) else ""
        self.DTX_PREFER16BIT="DTX_PREFER16BIT " if int(self.dtx_flags[6]) else ""
        self.DTX_FULLBRITE="DTX_FULLBRITE " if int(self.dtx_flags[7]) else ""
        self.DTX_LUMBUMPMAP="DTX_LUMBUMPMAP " if int(self.dtx_flags[11]) else ""
        self.DTX_BUMPMAP="DTX_BUMPMAP " if int(self.dtx_flags[12]) else ""
        self.DTX_CUBEMAP="DTX_CUBEMAP " if int(self.dtx_flags[13]) else ""
        self.DTX_32BITSYSCOPY="DTX_32BITSYSCOPY " if int(self.dtx_flags[14]) else ""
        self.DTX_PREFER5551="DTX_PREFER5551 " if int(self.dtx_flags[15]) else ""

        # Everything else
        self.unknown = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.surface_flag = int.from_bytes(bytes_.read(4), 'little', signed=True)
        self.texture_group = int.from_bytes(bytes_.read(1), 'little', signed=False)

        # if we are using 1-3 mipmaps instead of 4
        self.mipmaps_used = int.from_bytes(bytes_.read(1), 'little', signed=True)
        self.mipmaps_used = 4 if self.mipmaps_used == 0 else self.mipmaps_used

        self.bpp = int.from_bytes(bytes_.read(1), 'little', signed=True)
        self.non_s3tc_offset = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.ui_mipmap_offset = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.texture_priority = int.from_bytes(bytes_.read(1), 'little', signed=True)
        self.detail_scale = struct.unpack("<f",bytes_.read(4))[0]
        self.detail_angle = int.from_bytes(bytes_.read(2), 'little', signed=True)
        self.command_raw = bytes_.read(128)
        self.command_string = self.command_raw.decode()
        self.command_string = "" if int(self.command_string[0] == 0) else self.command_string

        # If light_flag is 1, we find LIGHTDEFS definition and read all the bytes to the end of file starting from 32nd byte
        # it's always 9 bytes of LIGHTDEF and 23 bytes of random data before the real information starting
        # Last byte is always 00 in case of light_flag/LIGHTDEF present in file, so we must exclude it for printing
        if self.light_flag == 1:
            # Reading the rest of the file after header
            self.file_data = bytes_.read()[164:]
            # Finding and reading tail of the file starting from LIGHTDEFS
            self.lightdef_raw = self.file_data[self.file_data.find(b'LIGHTDEFS'):]
            self.lightdef_string = self.lightdef_raw[32:-1].decode()
        else:
            self.lightdef_string = ""

if (args.read or args.table) and args.output:
    print("--read and --table arguments supported only with --input")
    exit()

if args.read and args.table:
    print("--read and --table arguments cannot be used simultaneously")
    exit()

# Reading input file
input_file=open(args.input, 'rb')

# Reading header like a stream of bytes and parsing
header = DtxHeader()
header.parse(io.BytesIO(input_file.read()))

# Dealing with errors of wrong file type or wrong DTX version
if header.filetype != 0:
    print("Wrong file type, not a DTX texture")
    exit()

if header.filetype == 0 and header.version != -5:
    print("Wrong DTX version")
    exit()

# For --read argument printing file information
if args.read:
    print("File Path: {}".format(args.input))
    print("File Type: {}, DTX version: {}, Size: {}x{}, Mipmaps Used: {}, Light Flag: {}".format(header.filetype, DTX_ver_Enum(header.version).name, header.width, header.height, header.mipmaps_used, header.light_flag))
    print("DTX Flags: {}: {}{}{}{}{}{}{}{}{}{}{}".format(header.dtx_flags, header.DTX_PREFER4444, header.DTX_NOSYSCACHE, header.DTX_SECTIONSFIXED, header.DTX_MIPSALLOCED, header.DTX_PREFER16BIT, header.DTX_FULLBRITE, header.DTX_LUMBUMPMAP, header.DTX_BUMPMAP, header.DTX_CUBEMAP, header.DTX_32BITSYSCOPY, header.DTX_PREFER5551))
    print("Unknown:   {}, Surface Flag: {}, Texture Group: {}, BPP: {}".format(header.unknown, header.surface_flag, header.texture_group, BPP_Enum(header.bpp).name))
    print("Non S3TC Offset: {}, UI Mipmap Offset: {}, Texture Priority: {}, Detail Scale/Angle: {}/{}".format(header.non_s3tc_offset, header.ui_mipmap_offset, header.texture_priority, header.detail_scale, header.detail_angle))
    print("Command String:  {}".format(header.command_string))
    # Printing only the real data of Light String if it present (starting from 32nd byte and till EOF-1) and decoding to ASCII string
    print("Light String:    {}".format(header.lightdef_string))

# Writing meta-information into new CSV file or adding into existing
if args.table:
    meta_table=open(args.table, 'a')

    # First row of the CSV file should always be names of the parameters
    if os.path.getsize(args.table) == 0:
        meta_table.writelines("Filename;Filetype;DTX_VERSION;Width;Height;Mipmaps Used;DTX Flags;DTX_PREFER4444;DTX_NOSYSCACHE;DTX_SECTIONSFIXED;DTX_MIPSALLOCED;DTX_PREFER16BIT;DTX_FULLBRITE;DTX_LUMBUMPMAP;DTX_BUMPMAP;DTX_CUBEMAP;DTX_32BITSYSCOPY;DTX_PREFER5551;Unknown;Surface Flag;Texture Group;BPP;Non S3TC Offset;UI Mipmap Offset;Texture Priority;Detail Scale;Detail Angle;Command String;Light String;\n")

    meta_table.writelines("{};{};{};{};{};{};'{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};\n".format(args.input, header.filetype, DTX_ver_Enum(header.version).name, header.width, header.height, header.mipmaps_used, header.dtx_flags, header.DTX_PREFER4444, header.DTX_NOSYSCACHE, header.DTX_SECTIONSFIXED, header.DTX_MIPSALLOCED, header.DTX_PREFER16BIT, header.DTX_FULLBRITE, header.DTX_LUMBUMPMAP, header.DTX_BUMPMAP, header.DTX_CUBEMAP, header.DTX_32BITSYSCOPY, header.DTX_PREFER5551, header.unknown, header.surface_flag, header.texture_group, BPP_Enum(header.bpp).name, header.non_s3tc_offset, header.ui_mipmap_offset, header.texture_priority, header.detail_scale, header.detail_angle, header.command_string,header.lightdef_string))
    meta_table.close()

# Transfering meta information between the files
if args.output:
    # Opening output file to write to
    output_file=open(args.output, 'r+b')
    # Setting offset to 12th byte (Number of mipmaps)
    input_file.seek(12)
    output_file.seek(12)
    # Writing first 14 bytes till Number of mipmaps used
    output_file.write(input_file.read(14))
    # Skipping BPP
    input_file.seek(27)
    output_file.seek(27)
    # Writing everything else till the end of header
    output_file.write(input_file.read(137))
    output_file.close()
    # Writing Light String if it is present
    if header.light_flag == 1:
        output_file=open(args.output, 'a+')
        output_file.write(header.lightdef_raw.decode())
        output_file.close()
    print("Transfering went successfully from {} to {}".format(args.input, args.output))

# Closing everything
input_file.close()