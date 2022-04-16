import sys

# argument with the path path to the file and file name
input_file=open(sys.argv[1], 'rb')

# reading input file header in HEX format. Reading 164 bytes
byte = input_file.read(164).hex()
    
# printing whole input file in HEX format for tests
print(byte)

# printing file type
# we need to count symbols as nibbles (half of byte). If I say to read bytes from 3 and 4 (counting from 1), I need to set it as 2:4
print(int(byte[:8],32))     #converting to int32

# checking DTX_VERSION, signed int32. Should be -5
DTX_VERSION = bytes.fromhex(byte[8:16])                             #converting to real python hex (like 0x)
DTX_VERSION = int.from_bytes(DTX_VERSION, 'little', signed=True)    #converting python hex to signed int32
print(DTX_VERSION)

# output_file=open(sys.argv[2], 'rb')
# outpit_file.write()

# The idea is: we need to transfer header information except for Width, Height, BPP
# If LightFlag = 1, we need to transfer the ending of the file started with LIGHTDEFS definition
# Since FileType and DTX_VERSION are always the same, we can start to transfer bytes from NumberOfMipmaps to NumberOfMipmapsUsed
# Let's read them
print(byte[24:52])
# Let's read BPP
print(byte[52:54])
print(int(byte[52:54],8))   #converting to int8

# Let's read everything after BPP
print(byte[54:328])