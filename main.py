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

    # Parsing only version for if/case logic of the script
    def head(self,bytes_):
        self.filetype = int.from_bytes(bytes_.read(4), 'little', signed=False)
        self.version = int.from_bytes(bytes_.read(4), 'little', signed=True)

    # Parsing the whole header for DTX v1
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

        self.unknown = int.from_bytes(bytes_.read(2), 'little', signed=False) # always 0, at least in NOLF1
        self.surface_flag = int.from_bytes(bytes_.read(4), 'little', signed=True)
        self.texture_group = int.from_bytes(bytes_.read(1), 'little', signed=False)

        # If this value is 0, we assume we use 4 default mipmaps embedded with texture. Can only be 0-3
        self.mipmaps_used = int.from_bytes(bytes_.read(1), 'little', signed=True)
        self.mipmaps_used = 4 if self.mipmaps_used == 0 else self.mipmaps_used
        self.alpha_cutoff = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.alpha_cutoff = self.alpha_cutoff - 128 if self.alpha_cutoff != 0 else self.alpha_cutoff
        self.alpha_average = int.from_bytes(bytes_.read(1), 'little', signed=False)

        # A lot of unknown values
        self.unk1 = int.from_bytes(bytes_.read(4), 'little', signed=False)
        self.unk2 = int.from_bytes(bytes_.read(4), 'little', signed=False)
        self.unk3 = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.unk4 = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.unk5 = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.unk6 = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.unk7 = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.unk8 = int.from_bytes(bytes_.read(2), 'little', signed=False)
        # If light_flag is 1, we find LIGHTDEFS definition and read all the bytes to the end of file starting from 32nd byte
        # It's always 9 bytes of LIGHTDEF and 23 bytes of random data before the real information starting
        # Last byte is always 00 in case of light_flag/LIGHTDEF present in file, so we must exclude it for printing
        if self.light_flag == 1:
            # Reading the rest of the file after header
            self.file_data = bytes_.read()[44:]
            # Finding and reading tail of the file starting from LIGHTDEFS
            self.lightdef_raw = self.file_data[self.file_data.find(b'LIGHTDEFS'):]
            self.lightdef_string = self.lightdef_raw[32:-1].decode('unicode_escape')
        else:
            self.lightdef_string = ""

    # Parsing the whole header for DTX v1.5
    def parsev15(self, bytes_):
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
        self.unknown1 = int.from_bytes(bytes_.read(2), 'little', signed=False)
        #self.surface_flag = int.from_bytes(bytes_.read(2), 'little', signed=True)
        self.surface_flag = "{:08b}".format(int.from_bytes(bytes_.read(1), 'little', signed=False)) + "{:08b}".format(int.from_bytes(bytes_.read(1), 'little', signed=False))
        self.DTX_Glass="DTX_Glass " if int(self.surface_flag[7]) else ""
        self.DTX_Metal="DTX_Metal " if int(self.surface_flag[6]) else ""
        self.DTX_Wood="DTX_Wood " if int(self.surface_flag[5]) else ""
        self.DTX_Stone="DTX_Stone " if int(self.surface_flag[4]) else ""
        self.DTX_Corrugated_Metal="DTX_Corrugated_Metal " if int(self.surface_flag[3]) else ""
        self.DTX_Liquid="DTX_Liquid " if int(self.surface_flag[2]) else ""
        self.DTX_Ice="DTX_Ice " if int(self.surface_flag[1]) else ""
        self.DTX_Plaster="DTX_Plaster " if int(self.surface_flag[0]) else ""
        self.DTX_Carpet="DTX_Carpet " if int(self.surface_flag[15]) else ""
        self.DTX_Concrete="DTX_Concrete " if int(self.surface_flag[14]) else ""
        self.DTX_Organic="DTX_Organic " if int(self.surface_flag[13]) else ""
        self.DTX_Grass="DTX_Grass " if int(self.surface_flag[12]) else ""
        self.DTX_Gravel="DTX_Gravel " if int(self.surface_flag[11]) else ""
        self.DTX_Dirt="DTX_Dirt " if int(self.surface_flag[10]) else ""
        self.DTX_Ceramic="DTX_Ceramic " if int(self.surface_flag[9]) else ""
        self.DTX_NeverMask="DTX_NeverMask " if int(self.surface_flag[8]) else ""
        self.unknown2 = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.texture_group = int.from_bytes(bytes_.read(1), 'little', signed=False)

        # If this value is 0, we assume we use 4 default mipmaps embedded with texture. Can only be 0-3
        self.mipmaps_used = int.from_bytes(bytes_.read(1), 'little', signed=True)
        self.mipmaps_used = 4 if self.mipmaps_used == 0 else self.mipmaps_used
        self.alpha_cutoff = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.alpha_cutoff = self.alpha_cutoff - 128 if self.alpha_cutoff != 0 else self.alpha_cutoff
        self.alpha_average = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.detail_scale = struct.unpack("<f",bytes_.read(4))[0]
        self.detail_angle = int.from_bytes(bytes_.read(2), 'little', signed=True)
        self.unknown3 = int.from_bytes(bytes_.read(2), 'little', signed=False)
        self.command_raw = bytes_.read(128)
        if int(self.command_raw[0]) == 0:
            self.command_string = ""
        else:
            self.command_string = self.command_raw.decode(errors='ignore').replace("\n","")
            #self.command_string = self.command_raw.decode('unicode_escape')
            #self.command_string = self.command_raw.hex()

        # If light_flag is 1, we find LIGHTDEFS definition and read all the bytes to the end of file starting from 32nd byte
        # It's always 9 bytes of LIGHTDEF and 23 bytes of random data before the real information starting
        # Last byte is always 00 in case of light_flag/LIGHTDEF present in file, so we must exclude it for printing
        if self.light_flag == 1:
            # Reading the rest of the file after header
            self.file_data = bytes_.read()[44:]
            # Finding and reading tail of the file starting from LIGHTDEFS
            self.lightdef_raw = self.file_data[self.file_data.find(b'LIGHTDEFS'):]
            self.lightdef_string = self.lightdef_raw[32:-1].decode('unicode_escape')
        else:
            self.lightdef_string = ""


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
        self.unknown = int.from_bytes(bytes_.read(2), 'little', signed=False) # always 0, at least in NOLF1
        self.surface_flag = int.from_bytes(bytes_.read(4), 'little', signed=True)
        self.texture_group = int.from_bytes(bytes_.read(1), 'little', signed=False)

        # If this value is 0, we assume we use 4 default mipmaps embedded with texture. Can only be 0-3
        self.mipmaps_used = int.from_bytes(bytes_.read(1), 'little', signed=True)
        self.mipmaps_used = 4 if self.mipmaps_used == 0 else self.mipmaps_used

        self.bpp = int.from_bytes(bytes_.read(1), 'little', signed=True)
        self.non_s3tc_offset = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.ui_mipmap_offset = int.from_bytes(bytes_.read(1), 'little', signed=False)
        self.texture_priority = int.from_bytes(bytes_.read(1), 'little', signed=True)
        self.detail_scale = struct.unpack("<f",bytes_.read(4))[0]
        self.detail_angle = int.from_bytes(bytes_.read(2), 'little', signed=True)

        # If first byte of the command row is 0, it's not used/not set
        self.command_raw = bytes_.read(128)
        if int(self.command_raw[0]) == 0:
            self.command_string = ""
        else:
            self.command_string = self.command_raw.decode('unicode_escape')

        # If light_flag is 1, we find LIGHTDEFS definition and read all the bytes to the end of file starting from 32nd byte
        # It's always 9 bytes of LIGHTDEF and 23 bytes of random data before the real information starting
        # Last byte is always 00 in case of light_flag/LIGHTDEF present in file, so we must exclude it for printing
        if self.light_flag == 1:
            # Reading the rest of the file after header
            self.file_data = bytes_.read()[164:]
            # Finding and reading tail of the file starting from LIGHTDEFS
            self.lightdef_raw = self.file_data[self.file_data.find(b'LIGHTDEFS'):]
            self.lightdef_string = self.lightdef_raw[32:-1].decode('unicode_escape')
        else:
            self.lightdef_string = ""

# Some warnings on incompatible arguments
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
header.head(io.BytesIO(input_file.read()))

# Dealing with errors of wrong file type or wrong DTX version
if header.filetype != 0:
    print("Wrong file type, not a DTX texture or it is a rare DTX v1 with Master Palette (Blood 2 had 5 files of those, and you need to use dtx1-mpalette.py on them)")
    exit()

# In NOLF there is BARON_ACTION.DTX file with mess in DTX version, but overall it's compatible file for DTX_VERSION_LT2.
if header.filetype == 0 and header.version != -5 and header.version != -3 and header.version != -2:
    print("Wrong/Broken DTX version (not -2 or -3 or -5). If you sure it's compatible DTX file (NOLF1 had such BARON_ACTION.DTX for example),")
    print("you can edit your file in HEX editor replacing 8 bytes at the start of the file by this:")
    print("DTX v1:   00 00 00 00 FE FF FF FF")
    print("DTX v1.5: 00 00 00 00 FD FF FF FF")
    print("DTX v2:   00 00 00 00 FB FF FF FF")
    exit()


if header.filetype == 0 and header.version == -3 and args.output:
    print("Wrong DTX version: {} ({}). Meta transfering is intended to work only with -5 (DTX_VERSION_LT2) and -2 (DTX_VERSION_LT1)".format(header.version, DTX_ver_Enum(header.version).name))
    exit()

# Closing file and reopening it for new parsing for its version
input_file.close()


input_file=open(args.input, 'rb')

if header.version == -2:
    header.parsev1(io.BytesIO(input_file.read()))

if header.version == -3:
    header.parsev15(io.BytesIO(input_file.read()))

if header.version == -5:
    header.parse(io.BytesIO(input_file.read()))

# For --read argument printing file information
# For DTX v1
if args.read and header.version == -2:
    print("File Path: {}".format(args.input))
    print("File Type: {}, DTX version: {}, Size: {}x{}, Mipmaps Used: {}, Light Flag: {}".format(header.filetype, DTX_ver_Enum(header.version).name, header.width, header.height, header.mipmaps_used, header.light_flag))
    print("DTX Flags: {}: {}{}{}{}".format(header.dtx_flags, header.DTX_DONT_MAP_MASTER, header.DTX_SECTIONSFIXED, header.DTX_ALPHA_MASK, header.DTX_FULLBRITE))
    print("Unknown:   {}, Surface Flag: {}, Texture Group: {}".format(header.unknown, header.surface_flag, header.texture_group))
    print("Software Alpha Cutoff: {}, Software Average Alpha: {}".format(header.alpha_cutoff,header.alpha_average))
    print("Unknown Values:        4+4 Bytes: {}/{}, 1+1+2 Bytes: {}/{}/{}, 1+1+2 Bytes: {}/{}/{}".format(header.unk1,header.unk2,header.unk3,header.unk4,header.unk5,header.unk6,header.unk7,header.unk8))
    print("Light String:          {}".format(header.lightdef_string))

# For DTX v1.5
if args.read and header.version == -3:
    print("File Path:     {}".format(args.input))
    print("File Type:     {}, DTX version:   {}, Size: {}x{}, Mipmaps Used: {}, Light Flag: {}".format(header.filetype, DTX_ver_Enum(header.version).name, header.width, header.height, header.mipmaps_used, header.light_flag))
    print("DTX Flags:     {}: {}{}{}{}".format(header.dtx_flags, header.DTX_DONT_MAP_MASTER, header.DTX_SECTIONSFIXED, header.DTX_ALPHA_MASK, header.DTX_FULLBRITE))
    print("Surface Flags: {}: {}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(header.surface_flag, header.DTX_Glass, header.DTX_Metal, header.DTX_Wood, header.DTX_Stone, header.DTX_Corrugated_Metal, header.DTX_Liquid, header.DTX_Ice, header.DTX_Plaster, header.DTX_Carpet, header.DTX_Concrete, header.DTX_Organic, header.DTX_Grass, header.DTX_Gravel, header.DTX_Dirt, header.DTX_Ceramic, header.DTX_NeverMask))
    print("Texture Group: {}".format(header.texture_group))
    print("Software Alpha Cutoff: {}, Software Average Alpha: {}, Detail Scale/Angle: {}/{}".format(header.alpha_cutoff,header.alpha_average, header.detail_scale, header.detail_angle))
    print("Unknown Values:  Unk1: {}, Unk2: {}, Unk3: {}".format(header.unknown1, header.unknown2, header.unknown3))
    print("Command String:        {}".format(header.command_string))
    print("Light String:          {}".format(header.lightdef_string))

# For DTX v2
if args.read and header.version == -5:
    print("File Path: {}".format(args.input))
    print("File Type: {}, DTX version: {}, Size: {}x{}, Mipmaps Used: {}, Light Flag: {}".format(header.filetype, DTX_ver_Enum(header.version).name, header.width, header.height, header.mipmaps_used, header.light_flag))
    print("DTX Flags: {}: {}{}{}{}{}{}{}{}{}{}{}".format(header.dtx_flags, header.DTX_PREFER4444, header.DTX_NOSYSCACHE, header.DTX_SECTIONSFIXED, header.DTX_MIPSALLOCED, header.DTX_PREFER16BIT, header.DTX_FULLBRITE, header.DTX_LUMBUMPMAP, header.DTX_BUMPMAP, header.DTX_CUBEMAP, header.DTX_32BITSYSCOPY, header.DTX_PREFER5551))
    print("Unknown:   {}, Surface Flag: {}, Texture Group: {}, BPP: {}".format(header.unknown, header.surface_flag, header.texture_group, BPP_Enum(header.bpp).name))
    print("Non S3TC Offset: {}, UI Mipmap Offset: {}, Texture Priority: {}, Detail Scale/Angle: {}/{}".format(header.non_s3tc_offset, header.ui_mipmap_offset, header.texture_priority, header.detail_scale, header.detail_angle))
    print("Command String:  {}".format(header.command_string))
    # Printing only the real data of Light String if it present (starting from 32nd byte and till EOF-1) and decoding to ASCII string
    print("Light String:    {}".format(header.lightdef_string))

# Writing meta-information into new CSV file or adding into existing for DTX v1
if args.table and header.version == -2:
    meta_table=open(args.table, 'a', encoding="utf-8")

    # First row of the CSV file should always be names of the parameters
    if os.path.getsize(args.table) == 0:
        meta_table.writelines("Filename;Filetype;DTX_VERSION;Width;Height;Mipmaps Used;DTX Flags;DTX_DONT_MAP_MASTER;DTX_SECTIONSFIXED;DTX_ALPHA_MASK;DTX_FULLBRITE;Unknown;Surface Flag;Texture Group;Software Alpha Cutoff;Software Average Alpha;Unknown1;Unknown2;Unknown3;Unknown4;Unknown5;Unknown6;Unknown7;Unknown8;Light String;\n")

    meta_table.writelines("\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"'{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\n".format(args.input, header.filetype, DTX_ver_Enum(header.version).name, header.width, header.height, header.mipmaps_used, header.dtx_flags, header.DTX_DONT_MAP_MASTER, header.DTX_SECTIONSFIXED, header.DTX_ALPHA_MASK, header.DTX_FULLBRITE, header.unknown, header.surface_flag, header.texture_group, header.alpha_cutoff, header.alpha_average, header.unk1, header.unk2, header.unk3, header.unk4, header.unk5, header.unk6, header.unk7, header.unk8, header.lightdef_string))
    meta_table.close()

# Writing meta-information into new CSV file or adding into existing for DTX v1.5
if args.table and header.version == -3:
    meta_table=open(args.table, 'a', encoding="utf-8")

    # First row of the CSV file should always be names of the parameters
    if os.path.getsize(args.table) == 0:
        meta_table.writelines("Filename;Filetype;DTX_VERSION;Width;Height;Mipmaps Used;DTX Flags;DTX_DONT_MAP_MASTER;DTX_SECTIONSFIXED;DTX_ALPHA_MASK;DTX_FULLBRITE;Surface Flag;Texture Group;Software Alpha Cutoff;Software Average Alpha;Detail Scale;Detail Angle;Unknown1;Unknown2;Unknown3;Command String;Light String;\n")

    meta_table.writelines("\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"'{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}:{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\n".format(args.input, header.filetype, DTX_ver_Enum(header.version).name, header.width, header.height, header.mipmaps_used, header.dtx_flags, header.DTX_DONT_MAP_MASTER, header.DTX_SECTIONSFIXED, header.DTX_ALPHA_MASK, header.DTX_FULLBRITE, header.surface_flag, header.DTX_Glass, header.DTX_Metal, header.DTX_Wood, header.DTX_Stone, header.DTX_Corrugated_Metal, header.DTX_Liquid, header.DTX_Ice, header.DTX_Plaster, header.DTX_Carpet, header.DTX_Concrete, header.DTX_Organic, header.DTX_Grass, header.DTX_Gravel, header.DTX_Dirt, header.DTX_Ceramic, header.DTX_NeverMask, header.texture_group, header.alpha_cutoff, header.alpha_average, header.detail_scale, header.detail_angle, header.unknown1, header.unknown2, header.unknown3, header.command_string, header.lightdef_string))
    meta_table.close()

# Writing meta-information into new CSV file or adding into existing for DTX v2
if args.table and header.version == -5:
    meta_table=open(args.table, 'a', encoding="utf-8")

    # First row of the CSV file should always be names of the parameters
    if os.path.getsize(args.table) == 0:
        meta_table.writelines("Filename;Filetype;DTX_VERSION;Width;Height;Mipmaps Used;DTX Flags;DTX_PREFER4444;DTX_NOSYSCACHE;DTX_SECTIONSFIXED;DTX_MIPSALLOCED;DTX_PREFER16BIT;DTX_FULLBRITE;DTX_LUMBUMPMAP;DTX_BUMPMAP;DTX_CUBEMAP;DTX_32BITSYSCOPY;DTX_PREFER5551;Unknown;Surface Flag;Texture Group;BPP;Non S3TC Offset;UI Mipmap Offset;Texture Priority;Detail Scale;Detail Angle;Command String;Light String;\n")

    meta_table.writelines("\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"'{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\"{}\";\n".format(args.input, header.filetype, DTX_ver_Enum(header.version).name, header.width, header.height, header.mipmaps_used, header.dtx_flags, header.DTX_PREFER4444, header.DTX_NOSYSCACHE, header.DTX_SECTIONSFIXED, header.DTX_MIPSALLOCED, header.DTX_PREFER16BIT, header.DTX_FULLBRITE, header.DTX_LUMBUMPMAP, header.DTX_BUMPMAP, header.DTX_CUBEMAP, header.DTX_32BITSYSCOPY, header.DTX_PREFER5551, header.unknown, header.surface_flag, header.texture_group, BPP_Enum(header.bpp).name, header.non_s3tc_offset, header.ui_mipmap_offset, header.texture_priority, header.detail_scale, header.detail_angle, header.command_string, header.lightdef_string))
    meta_table.close()

# Transfering meta information between the files for DTX v2
if args.output and header.version == -5:
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
    # Closing output file
    output_file.close()

    # Writing Light String if it is present. In this rare case we file reopen in append mode
    if header.light_flag == 1:
        output_file=open(args.output, 'a+')
        output_file.write(header.lightdef_raw.decode())
        output_file.close()
    
    # Printing results
    print("Transfering of DTX v2 went successfully from {} to {}".format(args.input, args.output))

# Transfering meta information between the files for DTX v1
if args.output and header.version == -2:
    # Opening output file to write to
    output_file=open(args.output, 'r+b')
    # Setting offset to 12th byte (Number of mipmaps)
    input_file.seek(12)
    output_file.seek(12)
    # Writing till the end of header, skipping all the unknown parameters
    # In case we'll want to rewrite unknown header parameters too, swap 16 to 32
    # output_file.write(input_file.read(32))
    output_file.write(input_file.read(16))
    # Closing output file
    output_file.close()

    # Writing Light String if it is present. In this rare case we file reopen in append mode
    if header.light_flag == 1:
        output_file=open(args.output, 'a+')
        output_file.write(header.lightdef_raw.decode())
        output_file.close()
    
    # Printing results
    print("Transfering of DTX v1 went successfully from {} to {}".format(args.input, args.output))

# Closing input file
input_file.close()