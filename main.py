import argparse
import sys

# all the available arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="Path and file name of the input DTX to read meta from")
parser.add_argument("-o","--output", help="Path and file name of the output DTX to transfer meto to")
parser.add_argument("-r","--read", help="Option to just read the input file",action="store_true")
args = parser.parse_args()

# reading input file
input_file=open(args.input, 'rb')

# reading input file header in HEX format. Reading 164 bytes
# byte = input_file.read(164).hex()
# readint inpit file header in Python HEX format. Readint 164 bytes
byte = input_file.read(164)
    
# printing whole input file in HEX format for tests
print(byte)

# printing file type
# we need to count symbols as nibbles (half of byte) in case of using hex() convertion. If I say to read bytes from 3 and 4 (counting from 1), I need to set it as 2:4
# so I removed this code to read file as raw bytes
print(int.from_bytes(byte[0:4], 'little', signed=False))     #converting to int32

# checking DTX_VERSION, signed int32. Should be -5
DTX_VERSION=int.from_bytes(byte[4:8], 'little', signed=True)
print(DTX_VERSION)

# output_file=open(sys.argv[2], 'rb')
# outpit_file.write()

# The idea is: we need to transfer header information except for Width, Height, BPP
# If LightFlag = 1, we need to transfer the ending of the file started with LIGHTDEFS definition
# Since FileType and DTX_VERSION are always the same, we can start to transfer bytes from NumberOfMipmaps to NumberOfMipmapsUsed
# Let's read them
print(byte[12:26])
# Let's read BPP
print(byte[26:27])
print(int.from_bytes(byte[26:27], 'little', signed=True))   #converting to int8

# Let's read everything after BPP to the end of header
print(byte[54:328])

if args.read:
    print('Filename=' + args.input)
    print('DTX_VERSION=' + str(DTX_VERSION) )
    print('Size=' + str(int.from_bytes(byte[8:10], 'little', signed=False)) + 'x' + str(int.from_bytes(byte[10:12], 'little', signed=False)))