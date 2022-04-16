import sys

# argument with the path path to the file and file name
input_file=open(sys.argv[1], 'rb')

# reading input file in HEX format
byte = input_file.read(164).hex()
    
# printing whole input file in HEX format for tests
print(byte)

# printing file type
print(int(byte[:8],32))

# checking DTX_VERSION, signed int32. Should be -5
DTX_VERSION = bytes.fromhex(byte[8:16])
DTX_VERSION = int.from_bytes(DTX_VERSION, 'little', signed=True)
print(DTX_VERSION)

# output_file=open(sys.argv[2], 'rb')
# outpit_file.write()