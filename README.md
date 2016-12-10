# DONT ASK ME FOR ROMS DONT ASK ME FOR ROMS 
# DONT ASK ME FOR ROMS DONT ASK ME FOR ROMS

# What it is
* tools to extract 8x8 and 16x16 'tiles' from cps2 EPROM files
* tools to write custom/modified graphics tiles to the EPROM files

# What it do (now)
* interleaves the 8 files that contain dumps from the EPROMs
into 2 files that can be opened in an external tile editor as 
'4bpp planar' with (16x16) rows interleaving
* deinterleaves theses 2 files, producing 8 files that can be written to your own EPROMs or whatever  
* converts the '4 bits per plane' codec into the 0-15 values that are used to  index a given palette
* converts 8x8 and 16x16 tiles to .bmp (for editing)
* stitches together multiple 16x16 tiles and converts this into a single image
* converts .bmp files for 8x8 tiles, 16x16 tiles, and larger 'stitched together' images into the 4bpp format

# What it todo
* create color .bmp files by providing a 16 color palette
* ?????
