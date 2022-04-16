import argparse
import sys
import struct

from sqlalchemy import null 

# all the available arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Path and file name of the input DTX to read meta from")
parser.add_argument("-o","--output", help="Path and file name of the output DTX to transfer meto to")
parser.add_argument("-r","--read", help="Option to just read the input file",action="store_true")
args = parser.parse_args()

# reading input file
input_file=open(args.input, 'rb')

# reading input file header in HEX format. Reading 164 bytes
byte = input_file.read(164)
    
# printing whole input file in HEX format for tests
print(byte)

# printing file type
# If I say to read bytes from 3 and 4 (counting from 1), I need to set it as 2:4
print(int.from_bytes(byte[0:4], 'little', signed=False))     #converting to int32

# checking DTX_VERSION, signed int32. Should be -5
DTX_VERSION=int.from_bytes(byte[4:8], 'little', signed=True)

# output_file=open(sys.argv[2], 'rb')
# outpit_file.write()

# The idea is: we need to transfer header information except for Width, Height, BPP
# If LightFlag = 1, we need to transfer the ending of the file started with LIGHTDEFS definition
# Since FileType and DTX_VERSION are always the same, we can start to transfer bytes from NumberOfMipmaps to NumberOfMipmapsUsed

# Let's read them
# print(byte[12:26])
# Let's read everything after BPP to the end of header
#print(byte[28:164])

if args.read:
    DTX_WIDTCH=int.from_bytes(byte[8:10], 'little', signed=False)
    DTX_HEIGHT=int.from_bytes(byte[10:12], 'little', signed=False)
    DTX_MIPMAPS_USED=int.from_bytes(byte[25:26], 'little', signed=True)
    if DTX_MIPMAPS_USED==0:
        DTX_MIPMAPS_USED=4
    DTX_USERFLAGS=int.from_bytes(byte[20:24], 'little', signed=True)
    DTX_TEXTURE_GROUP=int.from_bytes(byte[24:25], 'little', signed=False)
    DTX_BPP=int.from_bytes(byte[26:27], 'little', signed=True)
    DTX_NON_S3TC_OFFSET=int.from_bytes(byte[27:28], 'little', signed=False)
    DTX_UI_MIPMAP_OFFSET=int.from_bytes(byte[28:29], 'little', signed=False)
    DTX_TEXTURE_PRIORITY=int.from_bytes(byte[29:30], 'little', signed=False)
    DTX_DETAIL_SCALE=struct.unpack("<f",byte[30:34])[0]
    DTX_DETAIL_ANGLE=int.from_bytes(byte[34:36], 'little', signed=True)
    if int.from_bytes(byte[36:37], 'little', signed=True) == 0:
        DTX_COMMAND_STRING=""
    else:
        DTX_COMMAND_STRING=byte[36:164].decode()
    
    DTX_FLAGS="{:08b}".format(int.from_bytes(byte[16:17], 'little', signed=False))+"{:08b}".format(int.from_bytes(byte[17:18], 'little', signed=False))
    DTX_PREFER4444="DTX_PREFER4444 " if int(DTX_FLAGS[0]) else ""
    DTX_NOSYSCACHE="DTX_NOSYSCACHE " if int(DTX_FLAGS[1]) else ""
    DTX_SECTIONSFIXED="DTX_SECTIONSFIXED " if int(DTX_FLAGS[4]) else ""
    DTX_MIPSALLOCED="DTX_MIPSALLOCED " if int(DTX_FLAGS[5]) else ""
    DTX_PREFER16BIT="DTX_PREFER16BIT " if int(DTX_FLAGS[6]) else ""
    DTX_FULLBRITE="DTX_FULLBRITE " if int(DTX_FLAGS[7]) else ""
    DTX_LUMBUMPMAP="DTX_LUMBUMPMAP " if int(DTX_FLAGS[11]) else ""
    DTX_BUMPMAP="DTX_BUMPMAP " if int(DTX_FLAGS[12]) else ""
    DTX_CUBEMAP="DTX_CUBEMAP " if int(DTX_FLAGS[13]) else ""
    DTX_32BITSYSCOPY="DTX_32BITSYSCOPY " if int(DTX_FLAGS[14]) else ""
    DTX_PREFER5551="DTX_PREFER5551 " if int(DTX_FLAGS[15]) else ""

    print('Filename=' + args.input)
    print('DTX_VERSION=' + str(DTX_VERSION) )
    print('Size=' + str(DTX_WIDTCH) + 'x' + str(DTX_HEIGHT) )
    print('Mipmaps Used=' + str(DTX_MIPMAPS_USED))
    print('User Flags=' + str(DTX_USERFLAGS))
    print('Texture Group=' + str(DTX_TEXTURE_GROUP))
    print('BPP=' + str(DTX_BPP))
    print('Non S3TC Offset=' + str(DTX_NON_S3TC_OFFSET))
    print('UI Mipmap Offset=' + str(DTX_UI_MIPMAP_OFFSET))
    print('Texture Priority=' + str(DTX_TEXTURE_PRIORITY))
    print('Detail Scale=' + str(DTX_DETAIL_SCALE))
    print('Detail Angle=' + str(DTX_DETAIL_ANGLE))
    print('Command String=' + DTX_COMMAND_STRING)
    print('DTX Flags=' + DTX_FLAGS + ": " + DTX_PREFER4444 + DTX_NOSYSCACHE + DTX_SECTIONSFIXED + DTX_MIPSALLOCED + DTX_PREFER16BIT + DTX_FULLBRITE + DTX_LUMBUMPMAP + DTX_BUMPMAP + DTX_CUBEMAP + DTX_32BITSYSCOPY + DTX_PREFER5551)