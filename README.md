# DTX-Meta-Transfer
Transfer of DTX texture files meta-information

# Usage
python.exe main.py 
    -h, --help	Show help message
    -i INPUT, --input INPUT Path to the DTX we want to read
    -r, --read	Print DTX Meta information into console, requires --input option
    -t TABLE, --table TABLE Write DTX Meta information into CSV table, requires --input option

Example 
Reading meta information 
    python.exe main.py --input "C:\Textures\Example.DTX" --read

Writing meta information from several files to one CSV table
    python.exe main.py --input "C:\Textures\Example1.DTX" --table "C:\NOLF\out.csv"
    python.exe main.py --input "C:\Textures\Example2.DTX" --table "C:\NOLF\out.csv"
    python.exe main.py --input "C:\Textures\Example3.DTX" --table "C:\NOLF\out.csv"


# Useful links for LithTech engine and DTX format

DTX  
https://github.com/jsj2008/lithtech/blob/master/tools/shared/engine/dtxmgr.h  
I took research file for DTX v1 from here  
https://github.com/Five-Damned-Dollarz/DTXTool/blob/main/research/DTX_Lithtech_texture_template.bt

Research on DAT files for various versions of LithTech engine for 010 Editor  
https://github.com/haekb/godot-dat-reader/tree/master/Research

Predefined Surface Types for various games  
https://github.com/jsj2008/lithtech/blob/master/NOLF/Shared/SurfaceDefs.h  
https://github.com/jsj2008/lithtech/blob/master/Blood2/Shared/SharedDefs.h  
https://github.com/jsj2008/lithtech/blob/master/FEAR/Shared/SurfaceDefs.h  
https://github.com/jsj2008/lithtech/blob/master/NOLF2/Shared/SurfaceDefs.h  
https://github.com/jsj2008/lithtech/blob/master/Shogo/Shared/SurfaceTypes.h  

# LithTech versions
    Lithtech 1.0 (DAT v56), uses DTX v1
    	Shogo: Mobile Armor Division
    	Blood II: The Chosen
    	
    Lithtech 1.5 (DAT v57), uses DTX v1.5
    	Might and Magic IX
    	
    Kiss Psycho Circus (Custom 1.5) (DAT v127)
    	KISS: Psycho Circus: The Nightmare Child 
	
    Lithtech 2.x (DAT v66), uses DTX v2
    	NOLF1
    	Sanity: Aiken's Artifact 
    	Legends of Might and Magic
    	Die Hard: Nakatomi Plaza

    Lithtech PS2 (LTB v66)
    	NOLF1 (PS2)

    Lithtech Talon (DAT v70)
    	Aliens versus Predator 2
    	Might and Magic IX 

    Lithtech Jupiter (DAT v85) - template: bsp85.bt
    	No One Lives Forever 2: A Spy In H.A.R.M.'s Way
    	Tron 2.0
    	Medal of Honor: Pacific Assault
