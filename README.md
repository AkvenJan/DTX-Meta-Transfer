# DTX-Meta-Transfer
Transfer of LithTech engine DTX texture files meta-information

For now support added for DTX v2 version of the textures

The idea of transfering is to transfer all the embedded meta information of DTX textures (Flags, Surface Types, Details Scales, Command strings etc) from one DTX file to another, except for Width, Height and BPP.  
The main reason was: I was doing upscale pack for NOLF1 and needed to replace original textures with thousands of upscaled textured, which were batch converted from tga by dtxutil program. This way game was lacking detail textures, environment textures etc cause all this information was stored in original DTX files. So I wrote a python script to take this information and write into upscaled files. Because of dtxutil always use 32-Bit as image format - BPP information is not transfered.

# Usage
    python.exe main.py 
        -h, --help	Show help message
        -i INPUT, --input INPUT Path to the DTX we want to read
        -r, --read	Print DTX Meta information into console, requires --input option
        -t TABLE, --table TABLE Write DTX Meta information into CSV table, requires --input option

Example  
Reading meta information  
> python.exe main.py --input "C:\Textures\Example.DTX" --read
		
Writing meta information from several files to one CSV table  
> python.exe main.py --input "C:\Textures\Example1.DTX" --table "C:\NOLF\out.csv"  
> python.exe main.py --input "C:\Textures\Example2.DTX" --table "C:\NOLF\out.csv"  
> python.exe main.py --input "C:\Textures\Example3.DTX" --table "C:\NOLF\out.csv"

Transfering meta information between files  
> python.exe main.py --input "C:\Textures\Example1.DTX" --output "C:\Textures-Upscaled\Example1.DTX"

# Useful links for LithTech engine and DTX format

DTX  
https://github.com/jsj2008/lithtech/blob/master/tools/shared/engine/dtxmgr.h  
I took research file for DTX v1 from here  
https://github.com/Five-Damned-Dollarz/DTXTool/blob/main/research/DTX_Lithtech_texture_template.bt

Research on DAT files for various versions of LithTech engine for 010 Editor  
https://github.com/haekb/godot-dat-reader/tree/master/Research

Predefined Surface Types for various games  
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
