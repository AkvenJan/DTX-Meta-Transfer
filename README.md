# DTX-Meta-Transfer
Transfer of LithTech engine DTX texture files meta-information

For now support added for DTX v2 version of the textures for information reading and transfering and DTX v1 version only for for information reading

The idea of transfering is to transfer all the embedded meta information of DTX textures (Flags, Surface Types, Details Scales, Command strings etc) from one DTX file to another, except for Width, Height and BPP.  
The main reason was: I was doing upscale pack for NOLF1 and needed to replace original textures with thousands of upscaled textured, which were batch converted from tga by dtxutil program. This way game was lacking detail textures, environment textures etc cause all this information was stored in original DTX files. So I wrote a python script to extract this information from original files and write into upscaled files. Because of dtxutil always use 32-Bit as image format - BPP information is not transfered.

# Usage of DTX-Meta-Transfer
    python.exe main.py 
        -h, --help	Show help message
        -i INPUT, --input INPUT Path to the DTX we want to read
        -r, --read	Print DTX Meta information into console, requires --input option
        -t TABLE, --table TABLE Write DTX Meta information into CSV table, requires --input option

Example  
Reading meta information  
> python.exe main.py --input "C:\Textures\Example.DTX" --read
		
Writing meta information from several files to one CSV table (it will insert new rows into existing file or create new if there is none)  
> python.exe main.py --input "C:\Textures\Example1.DTX" --table "C:\NOLF\out.csv"  
> python.exe main.py --input "C:\Textures\Example2.DTX" --table "C:\NOLF\out.csv"  
> python.exe main.py --input "C:\Textures\Example3.DTX" --table "C:\NOLF\out.csv"

Transfering meta information between files  
> python.exe main.py --input "C:\Textures\Example1.DTX" --output "C:\Textures-Upscaled\Example1.DTX"

# DTX v1 Alpha Extraction
I also wrote a second script to extract alpha layer (first mipmap of it) from DTX v1 files. DTX v1 is an old format with all textures being paletted 8-bit images and alpha being stored inside DTX file. And none of existing editors supports this alpha viewing or extraction. So this script parse DTX file and write raw alpha image bytes into new file.  
Alpha data itself is stored as 4-bit (16 colors) grayscale image where every nibble contains number of color from the grayscale palette. Fox example, 4x4 pixels image would be stored as 16 nibbles. Also, for some reason DTX store this nibbles in reverted order so script will swap them for graphics editors to be able to work with this files. For example, the raw data of FA 18 would be saved by script as AF 81.  
Another example of 4x4 image in raw format  
FD EF CC DD FE 15 16 17 converted by script would be DF FE CC DD EF 51 61 71 and being interpreted as actual pixels in rows would be:  

    D F F E  
    C C D D  
    E F 5 1  
    6 1 7 1  

# Usage of DTX v1 Alpha Extraction
> python.exe dtx1-alpha.py --input CALEB1.dtx --output CALEB1.raw  
You'll get your raw pixel data, but you can't work with it, because now you need to convert this data into actual image. I used portable ImageMagick (https://imagemagick.org/script/download.php) for this. You'll need to know the exact size of the image you'll convert, so I suggest you use 010 Editor template for this to look into DTX file or use DTX-Meta-Transfer script with read or table arguments.
> convert.exe -size 256x256 -depth 4 gray:CALEB1.raw CALEB1.png  

# Notes on importing DTX v1 Alpha back to DEDIT (Level editor for LithTech 1.0)
Alpha image is extracted as 4-bit image but for elevel ditor to be able to use it its needs to be 8-bit paletted PCX with only 16 colors used upon importing.  
We'll use ImageMagick for this. I suggest we have 24-bit PNG as source. We'll convert it to 16 colors and use custom 16 colors grayscale palette. I put this 4bit.png into github for use, just don't forget to download it (it's just a 16x1 image with colors from 000000 to FFFFFF in a row).
> convert.exe -type Grayscale -colorspace gray +dither -depth 4 -colors 16 -remap 4bit.png PALMTREEM-alpha.png PALMTREEM-alpha.pcx

# Useful links for LithTech engine and DTX format

DTX  
https://github.com/jsj2008/lithtech/blob/master/tools/shared/engine/dtxmgr.h  
I took research file for DTX v1 from here  
https://github.com/Five-Damned-Dollarz/DTXTool/blob/main/research/DTX_Lithtech_texture_template.bt

Research on DAT files for various versions of LithTech engine for 010 Editor  
https://github.com/haekb/godot-dat-reader/tree/master/Research

Predefined Surface Types for various games (I also trying to put Surface Flags Types into research folder)  
NOLF  
https://github.com/jsj2008/lithtech/blob/master/NOLF/Shared/SurfaceDefs.h  
https://github.com/AkvenJan/DTX-Meta-Transfer/blob/main/research/NOLF-Surface.TXT  
Other games  
https://github.com/jsj2008/lithtech/blob/master/Blood2/Shared/SharedDefs.h  
https://github.com/jsj2008/lithtech/blob/master/FEAR/Shared/SurfaceDefs.h  
https://github.com/jsj2008/lithtech/blob/master/NOLF2/Shared/SurfaceDefs.h  
https://github.com/jsj2008/lithtech/blob/master/Shogo/Shared/SurfaceTypes.h  

# LithTech versions
    Lithtech 1.0 (DAT v56), uses DTX v1
    	Shogo: Mobile Armor Division
    	Blood II: The Chosen
    	
    Kiss Psycho Circus (Custom 1.5) (DAT v127), uses DTX v1.5
    	KISS: Psycho Circus: The Nightmare Child 
	
	Lithtech 1.5 (DAT v66), uses DTX v2
    	Might and Magic IX

    Lithtech 2.x (DAT v66), uses DTX v2
    	NOLF1
    	Sanity: Aiken's Artifact 
    	Legends of Might and Magic
    	Die Hard: Nakatomi Plaza

    Lithtech PS2 (LTB v66)
    	NOLF1 (PS2)

    Lithtech Talon (DAT v70), uses DTX v2
    	Aliens versus Predator 2

    Lithtech Jupiter (DAT v85), uses DTX v2
    	No One Lives Forever 2: A Spy In H.A.R.M.'s Way
    	Tron 2.0
    	Medal of Honor: Pacific Assault
