import argparse
import sys
import struct
import io

# Setting all the available arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Path and file name of the input DTX to read meta from")
parser.add_argument("-o","--output", help="Path and file name of the output DTX to transfer meto to")
parser.add_argument("-r","--read", help="Option to just read the input file",action="store_true")
args = parser.parse_args()

# Reading input file
input_file=open(args.input, 'rb')

# Reading header of the file. Thanks to Amphos
class DtxHeader(object):
    def __init__(self): # called on creation, set up some sane defaults
        self.filetype = 0
        self.version = -5
        self.width = -1
        self.height = -1
        self.mipmaps = 4

    # Parsing the whole header like a stream of bytes using research for DTX v2
    def parse(self, bytes_): # bytes_ is a byte stream, so it implicitly keeps place as you .read(n) from it
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
        self.command_string = bytes_.read(128).decode()
        self.command_string = "" if int(self.command_string[0] == 0) else self.command_string

# Reading header like a stream of bytes and parsing
header = DtxHeader()
header.parse(io.BytesIO(input_file.read(164)))

# For --read argument printing file information
if args.read:
    print("File Path: {}".format(args.input))
    print("File Type: {}, DTX_VERSION: {}, Size: {}x{}, Mipmaps Used: {}".format(header.filetype, header.version, header.width, header.height, header.mipmaps_used))
    print("DTX Flags: {}: {}{}{}{}{}{}{}{}{}{}{}".format(header.dtx_flags, header.DTX_PREFER4444, header.DTX_NOSYSCACHE, header.DTX_SECTIONSFIXED, header.DTX_MIPSALLOCED, header.DTX_PREFER16BIT, header.DTX_FULLBRITE, header.DTX_LUMBUMPMAP, header.DTX_BUMPMAP, header.DTX_CUBEMAP, header.DTX_32BITSYSCOPY, header.DTX_PREFER5551))
    print("Unknown:   {}, Surface Flag: {}, Texture Group: {}, BPP: {}".format(header.unknown, header.surface_flag, header.texture_group, header.bpp))
    print("Non S3TC Offset: {}, UI Mipmap Offset: {}, Texture Priority: {}, Detail Scale/Angle: {}/{}".format(header.non_s3tc_offset, header.ui_mipmap_offset, header.texture_priority, header.detail_scale, header.detail_angle))
    print("Command String:  {}".format(header.command_string))

    # If light_flag is 1, we find LIGHTDEFS definition and read all the bytes to the end of file starting from 32nd byte
    # it's always 9 bytes of LIGHTDEF and 23 bytes of random data before the real information starting
    # Last byte is always 00 in case of light_flag/LIGHTDEF present in file, so we must exclude it for printing
    if header.light_flag == 1:
        # Reading the whole file
        input_tail_byte = input_file.read()
        # Finding start position of LIGHTDEFS word
        litghdef_start = input_tail_byte.find(b'LIGHTDEFS')
        # Printing decoded part of Light information
        print("Light String:    {}".format(input_tail_byte[litghdef_start+32:-1].decode()))