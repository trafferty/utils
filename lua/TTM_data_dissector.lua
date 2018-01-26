--  Wireshark Dissector for CINC TTM data
--    Used for debugging TTM "delay" experienced 
--    during summer of 2017.  This version was used
--    after switch to UDP.
--
--    T.Rafferty - 08/01/2017
--
print("Loading dissector for TTM data...")
print("TTM host IP is "..TTM_Host_address)

-- create a "protocol" for our tree
ttm_proto = Proto("TTM","TTMData","TTM Data")

-- create new fields for TTM data
TTM_coarse_offset_F = ProtoField.string("ttm.coarse_offset", "Coarse offset (nm) ")
TTM_coarse_status_F = ProtoField.string("ttm.coarse_status", "Coarse status      ")
TTM_fine_offset_F   = ProtoField.string("ttm.fine_offset",   "Fine offset (nm)   ")
TTM_fine_status_F   = ProtoField.string("ttm.fine_status",   "Fine status        ")
TimeStamp_F         = ProtoField.string("ttm.time_stamp",    "Cam Time Stamp (ms)")
SerialNum_F         = ProtoField.string("ttm.serial_num",    "Serial Number      ")
PacketDelta_F       = ProtoField.string("ttm.packet_deltas", "Packet Delta (ms)  ")

--src_F = ProtoField.string("ttm.src","Source")
--dst_F = ProtoField.string("ttm.dst","Destination")

-- add our fields to the protocol
ttm_proto.fields = {TTM_coarse_offset_F, TTM_coarse_status_F, TTM_fine_offset_F, TTM_fine_status_F, TimeStamp_F, SerialNum_F, PacketDelta_F }

-- then register ttm_proto as a postdissector
register_postdissector(ttm_proto)

ip_src_f = Field.new("ip.src")
ip_dst_f = Field.new("ip.dst")
udp_src_f = Field.new("udp.srcport")
udp_dst_f = Field.new("udp.dstport")

-- initialization routine
local TTMCnt
local SerialNumber_prev
local TimeStamp_uSec_prev = {}
function ttm_proto.init ()
    TTMCnt = -1
    SerialNumber_prev = -1
    TimeStamp_uSec_prev[0] = 0
    TimeStamp_uSec_prev[1] = 0
    TimeStamp_uSec_prev[2] = 0
    TimeStamp_uSec_prev[3] = 0
end

function ttm_proto.dissector(buffer,pinfo,tree  )
    
    --if pinfo.visited then return end

    local udp_src = udp_src_f()
    local udp_dst = udp_dst_f()
    local ip_src = ip_src_f()
    local ip_dst = ip_dst_f()
    local src = ""
    local dst = ""

    if udp_src then
       src = tostring(ip_src) .. ":" .. tostring(udp_src)
       dst = tostring(ip_dst) .. ":" .. tostring(udp_dst)
    --    local subtree = tree:add(ttm_proto,"Yo")
    --    subtree:add(src_F,src)
    --    subtree:add(dst_F,dst)
    end

    -- As a reference, here is the c-struct in IMCS:
    --
    --  typedef struct {
    --    int16_t TTM_coarse_offset[4][2];  // 1nm/bit, +/- 32um
    --    int16_t TTM_coarse_status[4][2];  // 0:OK, other:NG
    --    int16_t TTM_fine_offset[4][2];    // 0.1nm/bit, +/- 3.2um
    --    int16_t TTM_fine_status[4][2];    // 0:OK, other:NG
    --    uint32_t SerialNum;               // Packet counter Starting from 0 increments by one each time.
    --    uint32_t TimeStamp_uSec[4];      //<- this is change 4 cameras time stamp LB,LF,RF,RB Time Stamp 
    --  } cam_meas_t;
    

    -- local camDataLength = 2 * 4 * 2

    -- Define byte offset within packet of where TTM data starts
    local buffer_offset = 42
    -- local cam1dataOffset = buffer_offset
    -- local cam2dataOffset = cam1dataOffset + camDataLength
    -- local cam3dataOffset = cam2dataOffset + camDataLength
    -- local cam4dataOffset = cam3dataOffset + camDataLength
    -- local serialNumOffset = cam4dataOffset + camDataLength
    -- local timeStamp1Offset = serialNumOffset + 4
    -- local timeStamp2Offset = timeStamp1Offset + 4
    -- local timeStamp3Offset = timeStamp2Offset + 4
    -- local timeStamp4Offset = timeStamp3Offset + 4
    -- local ttm_data_length = timeStamp4Offset + 4

    -- local buffer_length = buffer_offset + ttm_data_length

    --print("We think the TTM buff should be this long: ".. ttm_data_length)
    --print("buffer:len: ".. buffer:len())
   
    
    -- TTM_Host_address is setup in ~/.wireshark/init.lua.  it is typically "192.168.2.11:5259"
    if src == TTM_Host_address then

        local TTM_coarse_offset_X = {}
        local TTM_coarse_status_X = {}
        local TTM_fine_offset_X = {}
        local TTM_fine_status_X = {}
        local TTM_coarse_offset_Y = {}
        local TTM_coarse_status_Y = {}
        local TTM_fine_offset_Y = {}
        local TTM_fine_status_Y = {}
        local SerialNum = 0
        local SerialNumDelta = 0
        local TimeStamp_uSec = {}
        local TimeStampDelta_uSec = {}

        -- local log_tree = tree:add(ttm_proto,"Log Msgs")
        
        pinfo.cols.protocol = "TTMData"
        local packetnum = pinfo.number
        local ts = pinfo.rel_ts
        local delta_ts = pinfo.delta_dis_ts

        ptr = buffer_offset
        TTM_coarse_offset_X[0] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_offset_Y[0] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_offset_X[1] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_offset_Y[1] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_offset_X[2] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_offset_Y[2] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_offset_X[3] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_offset_Y[3] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_status_X[0] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_status_Y[0] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_status_X[1] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_status_Y[1] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_status_X[2] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_status_Y[2] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_status_X[3] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_coarse_status_Y[3] = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_fine_offset_X[0]   = buffer:range(ptr, 2):int() * 1e-1; ptr = ptr + 2
        TTM_fine_offset_Y[0]   = buffer:range(ptr, 2):int() * 1e-1; ptr = ptr + 2
        TTM_fine_offset_X[1]   = buffer:range(ptr, 2):int() * 1e-1; ptr = ptr + 2
        TTM_fine_offset_Y[1]   = buffer:range(ptr, 2):int() * 1e-1; ptr = ptr + 2
        TTM_fine_offset_X[2]   = buffer:range(ptr, 2):int() * 1e-1; ptr = ptr + 2
        TTM_fine_offset_Y[2]   = buffer:range(ptr, 2):int() * 1e-1; ptr = ptr + 2
        TTM_fine_offset_X[3]   = buffer:range(ptr, 2):int() * 1e-1; ptr = ptr + 2
        TTM_fine_offset_Y[3]   = buffer:range(ptr, 2):int() * 1e-1; ptr = ptr + 2
        TTM_fine_status_X[0]   = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_fine_status_Y[0]   = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_fine_status_X[1]   = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_fine_status_Y[1]   = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_fine_status_X[2]   = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_fine_status_Y[2]   = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_fine_status_X[3]   = buffer:range(ptr, 2):int(); ptr = ptr + 2
        TTM_fine_status_Y[3]   = buffer:range(ptr, 2):int(); ptr = ptr + 2

        SerialNum              = buffer:range(ptr, 4):uint(); ptr = ptr + 4
        TimeStamp_uSec[0]      = buffer:range(ptr, 4):uint() * 1e-3; ptr = ptr + 4
        TimeStamp_uSec[1]      = buffer:range(ptr, 4):uint() * 1e-3; ptr = ptr + 4
        TimeStamp_uSec[2]      = buffer:range(ptr, 4):uint() * 1e-3; ptr = ptr + 4
        TimeStamp_uSec[3]      = buffer:range(ptr, 4):uint() * 1e-3; ptr = ptr + 4
        TTMCnt = TTMCnt + 1

        SerialNumDelta         = SerialNum         - SerialNumber_prev     
        TimeStampDelta_uSec[0] = TimeStamp_uSec[0] - TimeStamp_uSec_prev[0]
        TimeStampDelta_uSec[1] = TimeStamp_uSec[1] - TimeStamp_uSec_prev[1]
        TimeStampDelta_uSec[2] = TimeStamp_uSec[2] - TimeStamp_uSec_prev[2]
        TimeStampDelta_uSec[3] = TimeStamp_uSec[3] - TimeStamp_uSec_prev[3]

        local coarse_offset = "("..TTM_coarse_offset_X[0]..", ".. TTM_coarse_offset_Y[0]..") ("
        coarse_offset = coarse_offset..TTM_coarse_offset_X[1]..", ".. TTM_coarse_offset_Y[1]..") ("
        coarse_offset = coarse_offset..TTM_coarse_offset_X[2]..", ".. TTM_coarse_offset_Y[2]..") ("
        coarse_offset = coarse_offset..TTM_coarse_offset_X[3]..", ".. TTM_coarse_offset_Y[3]..")"

        local coarse_status = "("..TTM_coarse_status_X[0]..", ".. TTM_coarse_status_Y[0]..") ("
        coarse_status = coarse_status..TTM_coarse_status_X[1]..", ".. TTM_coarse_status_Y[1]..") ("
        coarse_status = coarse_status..TTM_coarse_status_X[2]..", ".. TTM_coarse_status_Y[2]..") ("
        coarse_status = coarse_status..TTM_coarse_status_X[3]..", ".. TTM_coarse_status_Y[3]..")"

        local fine_offset = "("..TTM_fine_offset_X[0]..", ".. TTM_fine_offset_Y[0]..") ("
        fine_offset = fine_offset..TTM_fine_offset_X[1]..", ".. TTM_fine_offset_Y[1]..") ("
        fine_offset = fine_offset..TTM_fine_offset_X[2]..", ".. TTM_fine_offset_Y[2]..") ("
        fine_offset = fine_offset..TTM_fine_offset_X[3]..", ".. TTM_fine_offset_Y[3]..")"

        local fine_status = "("..TTM_fine_status_X[0]..", ".. TTM_fine_status_Y[0]..") ("
        fine_status = fine_status..TTM_fine_status_X[1]..", ".. TTM_fine_status_Y[1]..") ("
        fine_status = fine_status..TTM_fine_status_X[2]..", ".. TTM_fine_status_Y[2]..") ("
        fine_status = fine_status..TTM_fine_status_X[3]..", ".. TTM_fine_status_Y[3]..")"

        local time_stamp = string.format("%.2f (%.2f), %.2f (%.2f), %.2f (%.2f), %.2f (%.2f)", 
        TimeStamp_uSec[0], TimeStampDelta_uSec[0], TimeStamp_uSec[1], TimeStampDelta_uSec[1],
        TimeStamp_uSec[2], TimeStampDelta_uSec[2], TimeStamp_uSec[3], TimeStampDelta_uSec[3])

        local ttm_branch = tree:add(ttm_proto,buffer(),"TTM Data ("..tostring(ts)..", "..tostring(delta_ts)..") ")        
        ttm_branch:add(SerialNum_F, SerialNum.." (delta: "..SerialNumDelta..")")
        ttm_branch:add(TTM_coarse_offset_F, coarse_offset)
        ttm_branch:add(TTM_coarse_status_F, coarse_status)
        ttm_branch:add(TTM_fine_offset_F, fine_offset)
        ttm_branch:add(TTM_fine_status_F, fine_status)
        ttm_branch:add(TimeStamp_F, time_stamp)
        ttm_branch:add(PacketDelta_F, delta_ts*1000)

        local mean_x = (TTM_fine_offset_X[0] + TTM_fine_offset_X[1] + TTM_fine_offset_X[2] + TTM_fine_offset_X[3]) / 4.0
        local mean_y = (TTM_fine_offset_Y[0] + TTM_fine_offset_Y[1] + TTM_fine_offset_Y[2] + TTM_fine_offset_Y[3]) / 4.0

        local new_col_info = = string.format("[%d] SN: %d, Error: (%.1f, %.1f)", TTMCnt, SerialNum, mean_x, mean_y)

        if delta_ts > 0.02 then
            new_col_info = new_col_info.." ( Delay detected: ".. string.format("%.1f", delta_ts*1000) .. " ms)"
        end

        pinfo.cols.info = new_col_info
    
        SerialNumber_prev      = SerialNum        
        TimeStamp_uSec_prev[0] = TimeStamp_uSec[0]
        TimeStamp_uSec_prev[1] = TimeStamp_uSec[1]
        TimeStamp_uSec_prev[2] = TimeStamp_uSec[2]
        TimeStamp_uSec_prev[3] = TimeStamp_uSec[3]

    end    
end


