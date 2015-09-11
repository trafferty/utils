-- dissects the v49 Protocol (including the TGI specific fields)
packetnum = -1
v49_proto = Proto("v49","Vita49","Vita 49 Protocol")
-- create a function to dissect it
function v49_proto.dissector(buffer,pinfo,tree)
    pinfo.cols.protocol = "V49"
    cmd = buffer(0,4):le_uint()
   
    packetnum = pinfo.number

    local subtree_packet = tree:add(v49_proto,buffer(),"Vita 49 ("..buffer:len()..")")
   
    local subtree_header = subtree_packet:add_le(buffer(0,12), "V49 Header (7)")
   
    cmd_str = "unkown"
    if cmd == 1000 then
        cmd_str = "MSG2_HELLO"
    elseif cmd == 1001 then
        cmd_str = "MSG2_VERSION"
    elseif cmd == 1002 then
        cmd_str = "MSG2_FULL"
    elseif cmd == 1003 then
        cmd_str = "MSG2_BANNED"
    elseif cmd == 1004 then
        cmd_str = "MSG2_WELCOME"
    elseif cmd == 1005 then
        cmd_str = "MSG2_USE_VEHICLE"
    elseif cmd == 1006 then
        cmd_str = "MSG2_SPAWN"
    elseif cmd == 1007 then
        cmd_str = "MSG2_BUFFER_SIZE"
    elseif cmd == 1008 then
        cmd_str = "MSG2_VEHICLE_DATA"
    elseif cmd == 1009 then
        cmd_str = "MSG2_USER"
    elseif cmd == 1010 then
        cmd_str = "MSG2_DELETE"
    elseif cmd == 1011 then
        cmd_str = "MSG2_CHAT"
    elseif cmd == 1012 then
        cmd_str = "MSG2_FORCE"
    elseif cmd == 1017 then
        cmd_str = "MSG2_USER_CREDENTIALS"
    elseif cmd == 1019 then
        cmd_str = "MSG2_TERRAIN_RESP"
    elseif cmd == 1020 then
        cmd_str = "MSG2_WRONG_PW"
    elseif cmd == 1021 then
        cmd_str = "MSG2_RCON_LOGIN"
    elseif cmd == 1022 then
        cmd_str = "MSG2_RCON_LOGIN_FAILED"
    elseif cmd == 1023 then
        cmd_str = "MSG2_RCON_LOGIN_SUCCESS"
    elseif cmd == 1024 then
        cmd_str = "MSG2_RCON_LOGIN_NOTAV"
    elseif cmd == 1025 then
        cmd_str = "MSG2_RCON_COMMAND"
    elseif cmd == 1026 then
        cmd_str = "MSG2_RCON_COMMAND_FAILED"
    elseif cmd == 1027 then
        cmd_str = "MSG2_RCON_COMMAND_SUCCESS"
    end
   
    datasize = buffer(8,4):le_uint()
   
    pinfo.cols.info:set("Command: "..cmd_str)
    subtree_header:add_le(buffer(0,4),"command: ".. cmd_str .." (" .. cmd..")")
    subtree_header:add_le(buffer(4,4),"source: " .. buffer(4,4):le_uint())
    subtree_header:add_le(buffer(8,4),"size: " .. buffer(8,4):le_uint())

    databegin = 12
    dataend = databegin + datasize
    local subtree_data = subtree_packet:add_le(buffer(databegin,datasize), "V49 Data ("..datasize..")")
   
    if cmd == 1000 then
        local info = "RoR Version: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)

    elseif cmd == 1001 then
        local info = "RoR Version: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1002 then
        local info = "Server full! "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1003 then
        local info = "user banned! "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1004 then
        local info = "you are welcome. "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1007 then
        local info = "buffer size for vehicle data: "..buffer(databegin, datasize):le_uint()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1009 then
        local info = "deprecated rornet_2.0 packet"
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1010 then
        local info = "deleting user! "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1011 then
        local info = "chat: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1012 then
        local info = "force command (yet not used): "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1017 then
        subtree_data:add_le(buffer(databegin,20),"nickname: ".. buffer(databegin, 20):string())
        subtree_data:add_le(buffer(databegin+20,40),"SHA1 password: " .. buffer(databegin+20,40):string())
        subtree_data:add_le(buffer(databegin+60,40),"SHA1 uniqueID: " .. buffer(databegin+60,40):string())
    elseif cmd == 1019 then
        local info = "using terrain "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1020 then
        local info = "wrong password!"..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1021 then
        local info = "rcon login, with SHA1 password:"..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1022 then
        local info = "rcon login failed: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1023 then
        local info = "rcon login successful: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1024 then
        local info = "rcon not available: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1025 then
        local info = "rcon command: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1026 then
        local info = "rcon command failed: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1027 then
        local info = "rcon command successful: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
       
    elseif cmd == 1005 then
        local info = "Use vehicle: "..buffer(databegin, datasize):string()
        subtree_data:add_le(buffer(databegin, datasize), info)
    elseif cmd == 1008 then
        local oobtree = subtree_data:add(buffer(databegin+0,16), "OOB Data (16)")
        oobtree:add(buffer(databegin+0,4), "Time: "..buffer(databegin+0,4):le_uint())
        oobtree:add(buffer(databegin+4,4), "Engine Speed: "..buffer(databegin+4,4):le_uint())
        oobtree:add(buffer(databegin+8,4), "Engine Force: "..buffer(databegin+8,4):le_uint())
        local flagtree = oobtree:add(buffer(databegin+12,4), "Flags: "..buffer(databegin+12,4):le_uint())
        --flaghorn = buffer(12,4):le_uint() & 0x00000001
        --flagtree:add(buffer(12,4), "Horn: "..flaghorn)
        -- todo: all all others
       
        subtree_data:add(buffer(databegin+16,datasize-16), "Node Data ("..(datasize-16)..")")
       
       
    else
        local info = "Vita 49 Data ("..buffer:len()..")"..cmd
        local subtree = tree:add(v49_proto,buffer(),info)
        pinfo.cols.info:set(info)
    end
end
-- load the udp.port table
udp_table = DissectorTable.get("udp.port")
-- register our protocol to handle udp port 4201
tcp_table:add(4201,v49_proto)
