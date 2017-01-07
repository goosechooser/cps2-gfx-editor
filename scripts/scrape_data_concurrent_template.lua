local json = require("json")

SPRITE_START_ADDR = 0x0
RUN_LENGTH = 0x0

s = manager:machine().screens[":screen"]
cpu = manager:machine().devices[":maincpu"]
pal = manager:machine().devices[":palette"]
mem = cpu.spaces["program"]

--Sprite RAM is two 8K SRAMs:
--One mapped to 700000-707FFF and the other to 708000-70FFFF
function sprite_ram_pipe(start_addr, num_of_entries)
	local sprite_ = {}
	for i = 1, num_of_entries do
		offset = (i-1) * 0x8
		local index = tostring(i)
		local byte0 = string.format("%x", mem:read_u16(start_addr + offset)) 
		local byte1 = string.format("%x", mem:read_u16(start_addr + offset + 0x2))
		local byte2 = string.format("%x", mem:read_u16(start_addr + offset + 0x4))
		local byte3 = string.format("%x", mem:read_u16(start_addr + offset + 0x6))
		
		if check_bytes(byte0, byte1, byte2, byte3) then
			sprite_[index] = {byte0, byte1, byte2, byte3}
		end
	end
	return sprite_
end

--Filter out garbage data during the startup of the vsav rom
function check_bytes(byte0, byte1, byte2, byte3)
	local string_bytes = byte0 .. byte1 .. byte2 .. byte3
	local check1 = (string_bytes ~= "0000")
	local check2 = (string_bytes ~= "8000800080008000")
	local check3 = (string_bytes ~= "00ffffffff")
	return check1 and check2 and check3 and byte0 ~= nil and byte1 ~= nil and byte2 ~= nil and byte3 ~= nil
end

--Palette starts at 0x90C000 ends 0x3FF
function get_palettes(addr)
	palettes = {}
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

function pipe_out_data()
	local frame_number = s:frame_number()
	local sprites_ = sprite_ram_pipe(SPRITE_START_ADDR, RUN_LENGTH)
	
	if next(sprites_) ~= nil then
		local palettes_ = get_palettes(0x90C000)

		local frame = {
			frame_number = frame_number,
			sprites = sprites_,
			palette = palettes_
		}

		local encoded_table = json.encode(frame)
		io.write(encoded_table, "\n")

	end
end

emu.sethook(pipe_out_data, "frame")
