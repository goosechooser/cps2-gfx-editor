local json = require("json")

s = manager:machine().screens[":screen"]
cpu = manager:machine().devices[":maincpu"]
pal = manager:machine().devices[":palette"]
mem = cpu.spaces["program"]
--Palette starts at 0x90C000 ends 0x3FF
--Sprite bank starts 0x708000 ends 0x1FFF
--mem:read_u16

--Reads raw palette data and returns it
function read_all_palettes(addr)
	palettes_ = {}
	for i = 1, 32 do
		local hex_index = string.format("%x", i - 1)
		local row_offset = 0x20 * (i-1)
		
		local palette_ = {}
		for j=1, 16 do
			local color_offset = 0x2 * (j - 1)
			palette_[j] = string.format("%x", mem:read_u16(addr + row_offset + color_offset))
		end
		palettes[hex_index] = palette_
	end
	return palettes
end

--Checks for garbage sprite data that happens while the game is loading
function check_bytes(byte0, byte1, byte2, byte3)
	local string_bytes = byte0 .. byte1 .. byte2 .. byte3
	local check1 = (string_bytes ~= "0000")
	local check2 = (string_bytes ~= "8000800080008000")
	return check1 and check2
end

--Reads raw sprite data (see cps2tech.txt) and returns it
function read_sprite_ram(start_addr, num_of_entries)
	local sprite_ = {}
	for i = 1, num_of_entries do
		offset = (i-1) * 0x8
		
		local byte0 = string.format("%x", mem:read_u16(start_addr + offset)) 
		local byte1 = string.format("%x", mem:read_u16(start_addr + offset + 0x2))
		local byte2 = string.format("%x", mem:read_u16(start_addr + offset + 0x4))
		local byte3 = string.format("%x", mem:read_u16(start_addr + offset + 0x6))
		
		if check_bytes(byte0, byte1, byte2, byte3) then
			sprite_[i] = {byte0, byte1, byte2, byte3}
		end
	end
	return sprite_
end

function pipe_out()
	local frame_number = s:frame_number()
	local sprites_ = read_sprite_ram(0x708000, 2000)
	
	--If sprites_ isn't full of junk data
	if next(sprites_) ~= nil then
		local palettes_ = read_all_palettes(0x90C000)

		local frame = {
			frame_number = frame_number,
			sprites = sprites_,
			palette = palettes_
		}

		local encoded_table = json.encode(frame)
		io.write(encoded_table .. "\n")

	end
end

emu.sethook(pipe_out, "frame")

--The line below is how to hook a callback function to the closing/exiting of MAME
--emu.register_stop(pipe_done)

