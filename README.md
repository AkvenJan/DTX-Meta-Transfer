# DTX-Meta-Transfer
Transfer of LithTech engine DTX texture files meta-information

For now support added for information reading and transfering for DTX v1, DTX v2 versions of the textures. And DTX v1.5 version (Kiss: Psycho Circus: The Nightmare Child) for information reading only. Also alpha image extraction is available for DTX v1 and DTX v1.5 (DTX v2 doesn't need that, there is a converter from DTX v2 to TGA with alpha layer).

The idea of transfering is to transfer all the embedded meta information of DTX textures (Flags, Surface Types, Details Scales, Command strings etc) from one DTX file to another, except for Width, Height and BPP.  
The main reason was: I was doing upscale pack for NOLF1 and needed to replace original textures with thousands of upscaled textured, which were batch converted from tga by dtxutil program. This way game was lacking detail textures, environment textures etc cause all this information was stored in original DTX files. So I wrote a python script to extract this information from original files and write into upscaled files. Because of dtxutil always use 32-Bit as image format - BPP information is not transfered.  

DO NOT TRANSFER INFORMATION BETWEEN DIFFERENT VERSIONS OF THE FILES (from DTX v2 to DTX v1 and so on)!!!

You can read more about this format and ways of modding LithTech engine games in these two articles:  
https://www.moddb.com/members/akven/tutorials/upscaling-lithtech-engine-games  
https://www.moddb.com/mods/blood-ii-the-chosen-upscale-pack/tutorials/upscaling-lithtech-10-engine-games  

# Usage of DTX-Meta-Transfer
    python.exe main.py 
        -h, --help	Show help message
        -i INPUT, --input INPUT Path to the DTX we want to read
        -r, --read	Print DTX Meta information into console, requires --input option
        -t TABLE, --table TABLE Write DTX Meta information into CSV table, requires --input option
	-o OUTPUT, --output OUTPUT Path to the DTX we want to transfer meta-information to. We do not use --read or --table arguments with --output

Example  
Reading meta information  
> python.exe main.py --input "C:\Textures\Example.DTX" --read
		
Writing meta information from several files to one CSV table (it will insert new rows into existing file or create new if there is none)  
> python.exe main.py --input "C:\Textures\Example1.DTX" --table "C:\NOLF\out.csv"  
> python.exe main.py --input "C:\Textures\Example2.DTX" --table "C:\NOLF\out.csv"  
> python.exe main.py --input "C:\Textures\Example3.DTX" --table "C:\NOLF\out.csv"

Transfering meta information between files  
> python.exe main.py --input "C:\Textures\Example1.DTX" --output "C:\Textures-Upscaled\Example1.DTX"

# DTX v1 / DTX v1.5 Alpha Extraction
I also wrote a second script to extract alpha layer (first mipmap of it) from DTX v1 / DTX v1.5 files. DTX v1 / DTX v1.5 is an old format with all textures being paletted 8-bit images and alpha being stored inside DTX file. And none of existing editors supports this alpha viewing or extraction. So this script parse DTX file and write raw alpha image bytes into new file.  
Alpha data itself is stored as 4-bit (16 colors) grayscale image where every nibble contains number of color from the grayscale palette. Fox example, 4x4 pixels image would be stored as 16 nibbles. Also, for some reason DTX store this nibbles in reverted order so script will swap them for graphics editors to be able to work with this files. For example, the raw data of FA 18 would be saved by script as AF 81.  
Another example of 4x4 image in raw format  
FD EF CC DD FE 15 16 17 converted by script would be DF FE CC DD EF 51 61 71 and being interpreted as actual pixels in rows would be:  

    D F F E  
    C C D D  
    E F 5 1  
    6 1 7 1  

# Usage of DTX v1 / DTX v1.5 Alpha Extraction
> python.exe dtx1-alpha.py --input CALEB1.dtx --output CALEB1.raw  

You'll get your raw pixel data, but you can't work with it, because now you need to convert this data into actual image. I used portable ImageMagick (https://imagemagick.org/script/download.php) for this. You'll need to know the exact size of the image you'll convert, so I suggest you use 010 Editor template for this to look into DTX file or use DTX-Meta-Transfer script with read or table arguments.

> convert.exe -size 256x256 -depth 4 gray:CALEB1.raw CALEB1.png  

# Notes on importing DTX v1 / DTX v1.5 Alpha back to DEDIT (Level editor for LithTech 1.0 or LithTech 1.5)
Alpha image is extracted as 4-bit image but for level editor to be able to use it its needs to be 8-bit paletted PCX with only 16 colors used upon importing.  If you will create actual 4-bit image - DEDIT won't work with it.  
We'll use ImageMagick for this. I suggest we have 24-bit PNG as source. We'll convert it to 16 colors and use custom 16 colors grayscale palette. I put this 4bit.png into github for use, just don't forget to download it (it's just a 16x1 image with colors from 000000 to FFFFFF in a row).  
Example of this 4-bit palette  
![изображение](https://user-images.githubusercontent.com/72163549/173787428-d43159e9-99f1-4c13-95fa-a905ce042e61.png)  
Converting 24-bit PNG into 8-bit paletted PCX with custom 4-bit palette  
> convert.exe -type Grayscale -colorspace gray +dither -remap 4bit.png PALMTREEM-alpha.png PALMTREEM-alpha.pcx

This is an example of actual 8-bit PCX palette in file we created that will be imported by DEDIT without errors. All your real data needs to be represented by those 16 colors, everything else will be unused by DEDIT.  
![изображение](https://user-images.githubusercontent.com/72163549/173786872-7fa4c0eb-d29a-4919-9087-43a2b64a7f4c.png)

Alternative method  
I found an alternative method for editing which will create less human errors upon hand editing the files. Just use this palette  
![изображение](https://user-images.githubusercontent.com/72163549/202907071-8a1d5e22-0aa9-49c5-9c5c-f5e85deeb980.png)

It's stored in file 8bit.act. So if you need to edit your alpha images after they were converted from 24-bit PNG into 8-bit PCX - apply this palette first. This way you will get rid of cases when transparent (black) color occasionally was set to any other black color indexes upon editing. Engine do not check if your image grayscale or not - it just waits for paletted 8bit image.  

# DTX v1 Master Palette format
In Blood 2 (based on LithTech 1.0) there were 5 textures in really old format, maybe even not used by the engine anymore (CRATE1.DTX, GRYCRET1.DTX, METAL1.DTX, ORGBRIKB.DTX, DULL1_TRANS.DTX). In this format there is no palette information and image is stored just as 8-bit indexes to be used with external master palette. DEDIT do not understands this format, so there was no way to open them and look what inside. They even don't have any specific DTX meta in them. Using research file (https://github.com/AkvenJan/DTX-Meta-Transfer/blob/main/research/DTX-LithTech1.0%20Master%20Palette.bt) from  Amphos from LithFAQ discord I wrote a script to extract raw image from this files.

# Usage of DTX v1 Master Palette image extraction
> python.exe dtx1-mpalette.py --input CRATE1.dtx --output CRATE1.raw  

You'll get your raw pixel data, but you can't work with it, because now you need to convert this data into actual image. I used portable ImageMagick (https://imagemagick.org/script/download.php) for this. You'll need to know the exact size of the image you'll convert, so I suggest you use 010 Editor template for this to look into DTX file.  

> convert.exe -size 128x128 -depth 8 gray:CRATE1.raw CRATE1.png  

This way you'll get grayscale image. In Blood 2 expansion I found file TEXTURES_AO/MASTERPAL.DTX. And when I converted it to png, extracted it's palette and used it on DTX v1 master palette image - I get valid color image. For example (original grayscale texture and colored with master palette):  
![изображение](https://user-images.githubusercontent.com/72163549/177151850-667b22c5-01a8-4bf4-9c79-0a4f79ec1cba.png) CRATE1.DTX ![изображение](https://user-images.githubusercontent.com/72163549/177151934-0bf3ed68-2a92-41e1-8ffc-96386a05476f.png)

# Useful links for LithTech engine and DTX format

DTX  
https://github.com/jsj2008/lithtech/blob/master/tools/shared/engine/dtxmgr.h  
I took research file for general DTX v1 from here  
https://github.com/Five-Damned-Dollarz/DTXTool/blob/main/research/DTX_Lithtech_texture_template.bt  
Research on rare DTX v1 with Master Palette by Amphos from LithFAQ discord server

Research on DAT files for various versions of LithTech engine for 010 Editor  
https://github.com/haekb/godot-dat-reader/tree/master/Research

Predefined Surface Types for various games (I also trying to put Surface Flags Types into research folder)  
NOLF  
https://github.com/jsj2008/lithtech/blob/master/NOLF/Shared/SurfaceDefs.h  
[https://github.com/AkvenJan/DTX-Meta-Transfer/blob/main/research/Surface Flags - NOLF.TXT](<https://github.com/AkvenJan/DTX-Meta-Transfer/blob/main/research/Surface Flags - NOLF.TXT>)

Other games  
https://github.com/jsj2008/lithtech/blob/master/Blood2/Shared/SharedDefs.h  
https://github.com/jsj2008/lithtech/blob/master/FEAR/Shared/SurfaceDefs.h  
https://github.com/jsj2008/lithtech/blob/master/NOLF2/Shared/SurfaceDefs.h  
https://github.com/jsj2008/lithtech/blob/master/Shogo/Shared/SurfaceTypes.h  

# LithTech versions
Full list of LithTech games and file versions (constantly updated):  
https://docs.google.com/spreadsheets/d/1fm3vFc-qXiR5H2AYXzZlYu3q8DAfHz0I4PVrXrVfroA/edit?usp=sharing

Previous imperfect version (a lot of info was updated since):  
    Lithtech 1.0 (DAT v56), uses DTX v1
    	Shogo: Mobile Armor Division
    	Blood II: The Chosen
		Sanity: Aiken's Artifact (had some Lithtech 2.0 enhancements)

	Lithtech 1.0 (DAT v57), uses DTX v1
		TNN Outdoors Pro Hunter 2
    	
    Kiss Psycho Circus (Custom 1.5) (DAT v127), uses DTX v1.5
    	KISS: Psycho Circus: The Nightmare Child 
	
	Lithtech 1.5 (DAT v66), uses DTX v2  
    The engine is 1.5 but textures and levels are packed as LithTech 2x resourсes
    	Might and Magic IX

    Lithtech 2.x (DAT v66), uses DTX v2
    	NOLF1
    	Legends of Might and Magic
    	Die Hard: Nakatomi Plaza

    Lithtech PS2 (LTB v66), uses DTX v2 (mainly 32palletized)
    	NOLF1 (PS2)

    Lithtech Talon (DAT v70), uses DTX v2
    	Aliens versus Predator 2

    Lithtech Jupiter (DAT v85), uses DTX v2
    	No One Lives Forever 2: A Spy In H.A.R.M.'s Way
		Contract J.A.C.K.
    	Tron 2.0


| Game | Developer | Release Date | Engine | Version | Worlds | Models | Textures | DirectX | Comment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Shogo: Mobile Armor Division | Monolith Productions | 30.09.1998 | LithTech 1.0 | V1 | DAT v56 | ABC v6 | DTX v1 | 6 | |
| Blood II: The Chosen | Monolith Productions | 20.11.1998 | LithTech 1.0 | V1 | DAT v56 | ABC v6 | DTX v1 | 6 | |
| Blood II: The Nightmare Levels | Monolith Productions | 01.08.1999 | LithTech 1.0 | V1 | DAT v56 | ABC v6 | DTX v1 | 6 | |
| TNN Outdoors Pro Hunter 2 | Monolith Productions | 04.11.1999 | LithTech 1.2 | V1 | DAT v57 | ABC v6 | DTX v1 | 6 | |
| Ozymandias (machinima) | Strange Company | 1999 | LithTech 1.5 | V1 | DAT v57 | ABC v6 | DTX v1 | 6 | Was created with special software LithTech Film Producer. Engine is early version of LithTech 1.5 based on file versions. LithTech 1.5 was the first version of the engine licensed to third-party studios for game development. |
| Ozymandias Director's Cut (machinima) | Strange Company | 1999 | LithTech 1.5 | V1 | DAT v57 | ABC v6 | DTX v1 | 6 | Was created with special software LithTech Film Producer. Engine is early version of LithTech 1.5 based on file versions. LithTech 1.5 was the first version of the engine licensed to third-party studios for game development. The only different of Director's Cut is 6 different textures |
| KISS: Psycho Circus: The Nightmare Child | Third Law Interactive | 17.08.2000 | LithTech 1.5 | V1 | DAT v127 | ABC v6 | DTX v1.5 | 6 | |
| Vietnam: Black Ops | Fused Software | 27.09.2000 | LithTech 1.0 | V1 | DAT v56 | ABC v6 | DTX v1 | 6 | |
| Sanity: Aiken's Artifact | Monolith Productions | 03.11.2000 | LithTech 1.2 | V1 | DAT v57 | ABC v6 | DTX v1 | 7 | Had some Lithtech 2.0 rendering pipeline enhancements: like using DirectX 7 instead of DirectX 6 |
| Elite Forces: WWII - Normandy | Third Law Interactive/3LV Games | 31.01.2001 | LithTech 1.5 | V1 | DAT v127 | ABC v6 | DTX v1.5 | 6 | |
| Elite Forces: WWII - Iwo Jima | 3LV Games | 30.09.2001 | LithTech 1.5 | V1 | DAT v127 | ABC v6 | DTX v2 | 7 | Had some improvements over LithTech 1.5 like DTX v2 textures and DirectX 7. |
| Mini Golf Master 2 | 3LV Games | 12.10.2002 | LithTech 1.5 | V1 | DAT v127 | ABC v6 | DTX v1.5 | 6 | |
| The Operative: No One Lives Forever | Monolith Productions | 07.12.2000 | LithTech 2.0 | V2 | DAT v66 | ABC v12 | DTX v2 | 7 | Presumably was upgraded to LithTech 2.2 in patch v1.003 |
| Atlantis: The Lost Empire - Search for the Journal (free demo for Disney's Atlantis: The Lost Empire - Trial by Fire) | | 01.05.2001 | LithTech 2.2 | V2 | DAT v66 | ABC v13 | DTX v2 | 7 | |
| Atlantis: The Lost Empire - Trial by Fire | Zombie Inc. | 18.05.2001 | LithTech 2.2 | V2 | DAT v66 | ABC v13 | DTX v2 | 7 | |
| Tex Atomic's Big Bot Battles | Monolith Productions | 31.05.2001 | LithTech 2.2 ESD / RealArcade LithTech | V2 | DAT v66 | ABC v13 | DTX v2 | 7 | ESD - Entertainment Software Development |
| Legends of Might and Magic | New World Computing | 19.06.2001 | LithTech 2.2 | V2 | DAT v66 | ABC v13 | DTX v2 | 7 | |
| Vietnam 2: Special Assignment | Single Cell Software | 30.06.2001 | LithTech 2.2 | V2 | DAT v66 | ABC v12 | DTX v2 | 7 | |
| The Operative: No One Lives Forever (GOTY) | Monolith Productions | 05.10.2001 | LithTech 2.2 | V2 | DAT v66 | ABC v12 | DTX v2 | 7 | |
| Aliens Versus Predator 2 | Monolith Productions | 22.10.2001 | LithTech Talon | V2 | DAT v70 | ABC v12 | DTX v2 | 7 | |
| Alcatraz: Prison Escape | Zombie Inc. | 30.11.2001 | LithTech 2.2 | V2 | DAT v66 | ABC v13 | DTX v2 | 7 | |
| Global Operations | Barking Dog Studios | 25.03.2002 | LithTech 2.4 | V2 | DAT v66 | ABC v108 | DTX v2 | 8 | Early version of LithTech 2.4 before LTB format. Maybe some hybrid transition version 2.2>2.4 with DirectX 8 already but still with ABC format for models. Main game is DirectX 8 but executable also contains DirectDrawCreateEx import maybe for cinematics |
| Might and Magic IX | New World Computing | 28.03.2002 | LithTech 2.2 | V2 | DAT v66 | ABC v13 | DTX v2 | 7 | |
| Crisis Team: Ambulance Driver | Antidote Entertainment | 02.04.2002 | LithTech Talon/2.4 Hybrid | V2 | DAT v70 | LTB ABC/D3D v3 Body v14 | DTX v2 | 8 | Hybrid version with rendering pipeline from 2.4: DirectX 8 instead of DirectX 7. Do not use d3d.ren. Main game is DirectX 8 but executable also contains DirectDrawCreateEx import maybe for cinematics |
| Die Hard: Nakatomi Plaza | Piranha Games | 23.04.2002 | LithTech 2.4 | V2 | DAT v66 | LTB ABC/D3D v3 Body v13 | DTX v2 | 8 | Main game is DirectX 8 but executable also contains DirectDrawCreateEx import maybe for cinematics |
| The Operative: No One Lives Forever (PS2) | Monolith Productions / MumboJumbo | 29.04.2002 | LithTech Cobalt (LithTech PS2) | V2 | LTB v66 | LTB PS2 v16 | DTX v2 | N/A | |
| Elite Forces: Navy SEALs | Jarhead Games | 15.05.2002 | LithTech 2.4 | V2 | DAT v66 | LTB ABC/D3D v3 Body v13 | DTX v2 | 8 | Main game is DirectX 8 but executable also contains DirectDrawCreateEx import maybe for cinematics |
| Aliens versus Predator 2: Primal Hunt | Third Law Interactive | 13.08.2002 | LithTech Talon | V2 | DAT v70 | ABC v12 | DTX v2 | 7 | |
| Arthur's Quest: Battle for the Kingdom | 3LV Games | 21.08.2002 | LithTech Talon | V2 | DAT v70 | ABC v12 | DTX v2 | 7 | |
| Super Bubble Pop | Runecraft/Zombie Inc. | 01.12.2002 | LithTech 2.2 ESD / RealArcade LithTech | V2 | | | | | All the available version are not on LithTech engine at all. Maybe initial release was on LithTech ESD or some releases for consoles. Cannot find any info. |
| RailKings Model Railroad Simulator | Incagold GmbH | 04.12.2002 | LithTech 2.4 | V2 | DAT v66 | LTB ABC/D3D v3 Body v13 | DTX v2 | 8 | |
| CTU: Marine Sharpshooter | Jarhead Games | 20.03.2003 | LithTech 2.4 | V2 | DAT v66 | LTB ABC/D3D v3 Body v13 | DTX v2 | 8.1 | Some late custom variant of engine with DirectX 8.1 |
| Nina: Trylogia | Detalion | 16.12.2002 | LithTech Talon | V2 | DAT v70 | ABC v12 | DTX v2 | 7 | Initial Polish release of Nina: Agent Chronicles with some level differences |
| Nina: Agent Chronicles | Detalion | 08.04.2003 | LithTech Talon | V2 | DAT v70 | ABC v12 | DTX v2 | 7 | |
| Purge | Freeform Interactive | 15.04.2003 | LithTech Talon | V2 | DAT v70 | ABC v12 | DTX v2 | 7 | MMO |
| Aliens Versus Predator 2: Gold Edition | Monolith Productions / Third Law Interactive | 30.05.2003 | LithTech Talon | V2 | DAT v70 | ABC v12 | DTX v2 | 7 | |
| Navy SEALs: Weapons of Mass Destruction | Jarhead Games | 18.07.2003 | LithTech 2.4 | V2 | DAT v66 | LTB ABC/D3D v3 Body v13 | DTX v2 | 8.1 | Some late custom variant of engine with DirectX 8.1 |
| March! Offworld Recon | HBM Ltd | 11.09.2003 | LithTech Talon | V2 | DAT v70 | ABC v12 | DTX v2 | 7 | Games engine uses DirectX 7. But launcher application "march.exe" is DirectX 8.1 - launcher is not needed for the game to run |
| Western Outlaw: Wanted Dead or Alive | Jarhead Games | 28.09.2003 | LithTech 2.4 | V2 | DAT v66 | LTB ABC/D3D v3 Body v13 | DTX v2 | 8.1 | Some late custom variant of engine with DirectX 8.1 |
| The Matrix Online | Monolith Productions | 22.03.2005 | LithTech Discovery | V2 | | | | 9 | Highly customized engine version with its own formats. PKB for archives insead of REZ |
| Sniper: Path of Vengeance | Mirage Interactive | 19.09.2002 | LithTech 2.4/Jupiter | V3 | DAT v83/v85 | LTB v9 Mesh v23 | DTX v2 | 8 | Early version of engine without DirectX 8.1. Uses icon from 2.4 |
| No One Lives Forever 2: A Spy In H.A.R.M.'s Way Beta 39.1 (TO2 Development Build 39.1 / Jupiter v51) | | 13.03.2002 | LithTech Jupiter | V3 | DAT v81 | LTB v9 Mesh v18 | DTX v2 | 8.1 | Beta versions used LithTech 2.4 icon, on Jupiter build 51 CD |
| No One Lives Forever 2: A Spy In H.A.R.M.'s Way | Monolith Productions | 01.10.2002 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| No One Lives Forever 2: A Spy In H.A.R.M.'s Way v1.3 (Jupiter v69) | | 18.01.2006 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | Game version 1.3, came with Jupiter build 69 CD |
| Gods and Generals | AniVision | 01.03.2003 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| Mistmare | Arxel Tribe/Sinister Systems | 07.03.2003 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| Heat Project (MMO) | DOOBIC Entertainment | 14.05.2003 | LithTech Jupiter | V3 | | | | | The game is an MMO whose servers have already been shut down. There is no way to download the original client version to check the file formats. |
| Rubies of Eventide (MMO) | Cyber Warrior | 02.06.2003 | LithTech Jupiter | V3 | | | | | The game is an MMO whose servers have already been shut down. There is no way to download the original client version to check the file formats. |
| Tron 2.0 | Monolith Productions | 26.08.2003 | Lithtech Triton | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 9 | |
| Contract J.A.C.K. | Monolith Productions | 11.11.2003 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| Mysterious Journey II: Chameleon / Schizm II: Chameleon | Detalion | 24.11.2003 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| JunkMetal (MMO) | ENIX | 12.04.2004 | LithTech Jupiter | V3 | | | | | The game is an MMO whose servers have already been shut down. There is no way to download the original client version to check the file formats. |
| Mob Enforcer | Touchdown Entertainment | 11.06.2004 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| Marine Sharpshooter II: Jungle Warfare | Jarhead Games | 22.06.2004 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| World War II: Sniper - Call to Victory | Jarhead Games | 09.10.2004 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| GunGriffon: Allied Strike (Xbox) | Game Arts Co., Ltd | 14.12.2004 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | N/A | |
| Sentinel: Descendants in Time / (Realms of Illusion 2005-release) | Detalion | 14.12.2004 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| Army Ranger: Mogadishu | Jarhead Games | 14.06.2005 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 8.1 | |
| Sudden Attack (MMO) | Nexon Games | 23.08.2005 | LithTech Jupiter | V3 | | | | | The game is an MMO whose servers have already been shut down. There is no way to download the original client version to check the file formats. |
| Face of Mankind (MMO) | Duplex Systems/Nexeon Technologies | 27.03.2006 | LithTech Jupiter | V3 | | | | | The game is an MMO whose servers have already been shut down. There is no way to download the original client version to check the file formats. |
| Terrawars: New York Invasion | Ladyluck Digital Media | 28.06.2006 | LithTech Jupiter | V3 | DAT v85 | LTB v9 Mesh v23 | DTX v2 | 9 | Some late custom variant of engine with DirectX 9 |
| Combat Arms (MMO) | Doobic Studios | 11.06.2008 | LithTech Jupiter | V3 | | | | | The game is an MMO whose servers have already been shut down. There is no way to download the original client version to check the file formats. |
| Привидения из Букленда. Книжное приключение (Ghosts of Bookland) | PiPE Studio | 12.12.2008 | LithTech Jupiter | V3 | | | | | |
| F.E.A.R. | Monolith Productions | 18.10.2005 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Condemned: Criminal Origins | Monolith Productions | 22.11.2005 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. Combat | Monolith Productions | 17.8.2006 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. Extraction Point | TimeGate Studios/Monolith Productions | 24.10.2006 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. Gold Edition | TimeGate Studios/Monolith Productions | 20.03.2007 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Crossfire | Smilegate Entertainment | 03.05.2007 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Wolf Team | Softnyx | 01.09.2007 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. Perseus Mandate | TimeGate Studios/Monolith Productions | 06.11.2007 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. Platinum Collection | TimeGate Studios/Monolith Productions | 06.11.2007 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. Files (XBOX 360) | Day 1 Studios | 06.11.2007 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Terrorist Takedown 2: US Navy SEALs | City Interactive | 04.12.2007 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Operation Thunderstorm | City Interactive | 19.03.2008 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Mortyr: Operation Thunderstorm | City Interactive | 19.03.2008 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Combat Arms: Reloaded | Nexon Games | 11.07.2008 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Code of Honor 2: Conspiracy Island | City Interactive | 29.07.2008 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| SAS: Secure Tomorrow | City Interactive | 30.09.2008 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| The Royal Marines Commando | City Interactive | 15.11.2008 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Armed Forces Corp. | City Interactive | 27.02.2009 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Battlestrike: Shadow of Stalingrad | City Interactive | 17.07.2009 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Code of Honor 3: Desperate Measures | City Interactive | 28.07.2009 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Wolfschanze II | City Interactive | 24.11.2009 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Special Forces | City Interactive | 15.03.2010 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Terrorist Takedown 3 | City Interactive | 04.04.2010 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Repulse | Queen's Days Studio | 01.02.2012 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Gotham City Impostors | Monolith Productions | 07.02.2012 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| District 187: Sin Streets | CJ GameLab | 20.11.2012 | LithTech Jupiter Ex | V4 | | | | | Not alalyzing games past LithTech Jupiter |
| Condemned 2: Bloodshot | Monolith Productions | 11.03.2008 | LithTech Jupiter Ex V5 | V5 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. 2: Project Origin | Monolith Productions | 10.02.2009 | LithTech Jupiter Ex V5 | V5 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. 2: Reborn | Monolith Productions | 03.09.2009 | LithTech Jupiter Ex V5 | V5 | | | | | Not alalyzing games past LithTech Jupiter |
| F.E.A.R. Online | Inplay Interactive | 17.10.2014 | LithTech Jupiter Ex V5 | V5 | | | | | Not alalyzing games past LithTech Jupiter |
| Middle-earth: Shadow of Mordor | Monolith Productions | 30.09.2014 | LithTech Jupiter Ex V6 | V6 | | | | | Not alalyzing games past LithTech Jupiter |
| Middle-earth: Shadow of War | Monolith Productions | 10.10.2017 | Firebird Engine | V7 | | | | | Not alalyzing games past LithTech Jupiter |